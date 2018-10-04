import xworkflows

from model_utils import FieldTracker

from django.db import models

from .transition import TransitionEvent


class BaseStateDescription(xworkflows.Workflow):
    """
    Placeholder class
    """
    states = ()
    transitions = ()
    initial_state = None


class BaseStateMachine(xworkflows.WorkflowEnabled):
    """
    Workflow-enabled class that will be instantiated by the model each time
    a transition is performed.
    """
    # States from which submission cannot change state anymore
    final_states = []
    # States in which changing submission data is allowed
    editable_data_states = []

    state = BaseStateDescription()

    def __init__(self, model_instance):
        # We need this to add a back-reference to the model using this object
        self.model_instance = model_instance
        super().__init__()

    @property
    def finished(self):
        return self.state in self.final_states

    @property
    def data_changes_allowed(self):
        return self.state in self.editable_data_states


class BaseWorkflow(models.Model):
    """
    Model used to persist state changes.
    """
    class StateDoesNotExist(Exception):
        pass

    class TransitionDoesNotExist(Exception):
        pass

    class TransitionNotAvailable(Exception):
        pass

    # We will init this and run checks and custom logic for each state change
    WORKFLOW_CLASS = BaseStateMachine

    # States will be accessed through properties to enable custom logic on them
    _current_state = models.CharField(
        max_length=64, null=True, blank=True, db_column='current_state'
    )
    # We need previous_state for un-recalling submissions
    _previous_state = models.CharField(
        max_length=64, null=True, blank=True, db_column='previous_state'
    )

    tracker = FieldTracker()

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, value):
        """
        Changing current_state also changes previous_state as a side effect.
        All state changes trigger an automatic save().

        Changing the state is done by calling the appropriate transition
        (if available) on the related workflow-enabled object (self.workflow).

        """
        workflow = self.workflow
        if value not in workflow.state.workflow.states:
            raise self.StateDoesNotExist(
                f'No state named {value} in current workflow'
            )

        transition_name = None
        for t in workflow.state.transitions():
            if value == t.target.name:
                transition_name = t
                break
        if transition_name is None:
            raise self.TransitionNotAvailable(
                f'No transition to reach {value} from current state'
            )

        transition = getattr(workflow, transition_name)

        if not transition.is_available():
            raise self.TransitionNotAvailable('Transition checks not satisfied')

        # Call the transition; this should work (bar exceptions in pre-post
        # transition hooks)
        transition()

        # If everything went OK, persist the result and the transition.
        self._previous_state = self._current_state
        self._current_state = workflow.state.name
        TransitionEvent.objects.create(
            submission=self.submission,
            transition=transition_name,
            from_state=self._previous_state,
            to_state=self._current_state,
        )
        self.save()

    @property
    def previous_state(self):
        """
        Previous state will only be changed indirectly when changing
        current_state.
        """
        return self._previous_state

    @property
    def workflow(self):
        # Create workflow instance and set last *persisted* state on it
        wf = self.WORKFLOW_CLASS(model_instance=self)
        state = self.tracker.previous('_current_state') \
            if self.tracker.has_changed('_current_state') \
            else self.current_state
        wf.state = state
        return wf

    @property
    def data_changes_allowed(self):
        """
        Check whether data changes are allowed in current state.
        """
        return self.workflow.data_changes_allowed

    @property
    def available_transitions(self):
        """
        List of transitions that can be performed from current state.
        No pre-transition checks are taken into account at this point.

        """
        return [
            transition.name for transition in self.workflow.state.transitions()
        ]

    @property
    def available_states(self):
        """
        List of states that can be reached directly from current state.
        No pre-transition checks are taken into account at this point.

        """
        return [t.target.name for t in self.workflow.state.transitions()]

    def call_transition(self, trans_name):
        """
        Interface for calling a specific transition name on the workflow.

        It automatically persists the previous and new states.

        """
        # Call this now so we don't recreate the self.workflow object ad nauseam
        workflow = self.workflow

        # This is a `TransitionList` and supports the `in` operator
        if trans_name not in workflow.state.workflow.transitions:
            raise self.TransitionDoesNotExist(
                f'Transition {trans_name} does not exist in this workflow'
            )

        # This is a list of `Transition`s and doesn't support the `in` operator
        # without explicitly referencing `name`
        if trans_name not in [t.name for t in workflow.state.transitions()]:
            raise self.TransitionNotAvailable(
                f'Transition {trans_name} does not start from current state'
            )

        # Transition names are available as attributes on the workflow object
        transition = getattr(workflow, trans_name)

        if not transition.is_available():
            raise self.TransitionNotAvailable('Transition checks not satisfied')

        # Call the transition; this should work (bar exceptions in pre-post
        # transition hooks)
        transition()

        # If everything went OK, persist the result and the transition.
        self._previous_state = self._current_state
        self._current_state = workflow.state.name
        TransitionEvent.objects.create(
            submission=self.submission,
            transition=trans_name,
            from_state=self._previous_state,
            to_state=self._current_state,
        )
        self.save()

    def save(self, *args, **kwargs):
        # Set current state to initial state on first save if not there
        self._current_state = self._current_state or \
                              self.workflow.state.workflow.initial_state.name
        super().save(*args, **kwargs)
