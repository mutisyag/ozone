import enum

from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models, transaction

from model_utils import FieldTracker

from ozone.users.models import User

from .party import Party
from .workflows.base import BaseWorkflow
from .workflows.default import DefaultArticle7Workflow
from .workflows.accelerated import AcceleratedArticle7Workflow

__all__ = [
    'ReportingPeriod',
    'Obligation',
    'Submission',
    'TransitionEvent'
]


class ReportingPeriod(models.Model):
    """
    Period for which data is submitted.

    There is definitely a need to support non-standard reporting periods.
    """

    # TODO: how will these be used in the event of one-time reports?
    # The system could create a custom period based on the date(s) the transfer
    # took place, but that seems a bit overkill.

    # This will usually be '2017', '2018' etc; most periods (but not all!)
    # are mapped to calendar years
    name = models.CharField(max_length=64, unique=True)
    # indicates a "normal" (yearly) reporting period, to avoid need of extra
    # logic on the `name` field
    is_year = models.BooleanField(default=True)

    # this is always required, and can be in the future
    start_date = models.DateField()

    # we are always working with 'closed' reporting periods
    # TODO: is above assumption really true? what about one-time reports?
    end_date = models.DateField()

    description = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.name


class Obligation(models.Model):
    """
    TODO: analysis!
    """

    name = models.CharField(max_length=256, unique=True)
    # TODO: obligation-party mapping!

    description = models.CharField(max_length=256, blank=True)

    is_continuous = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Submission(models.Model):
    """
    One specific data submission (version!)
    """

    @enum.unique
    class SubmissionMethods(enum.Enum):
        """
        Enumeration of submission types
        """
        WEBFORM = 'Web form'
        EMAIL = 'Email'

    class StateDoesNotExist(Exception):
        pass

    class TransitionDoesNotExist(Exception):
        pass

    class TransitionNotAvailable(Exception):
        pass

    # This keeps a mapping between the DB-persisted workflow and
    # its actual implementation class.
    WORKFLOW_MAP = {
        'empty': None,
        'base': BaseWorkflow,
        'default': DefaultArticle7Workflow,
        'accelerated': AcceleratedArticle7Workflow
    }

    # TODO: this implements the `submission_type` field from the
    # Ozone Business Data Tables. Analyze how Party-to-Obligation/Version
    # mappings should be modeled.
    obligation = models.ForeignKey(
        Obligation, related_name='submissions', on_delete=models.PROTECT
    )

    # TODO (related to the above):
    # It looks like the simplest (best?) solution for handling
    # reporting format changes (i.e. schema versions) is to keep separate
    # models&tables for each such version.
    # Should investigate whether what's described above is a sane solution.
    schema_version = models.CharField(max_length=64)

    reporting_period = models.ForeignKey(
        ReportingPeriod, related_name='submissions', on_delete=models.PROTECT
    )

    # `party` is always the Party for which data is reported
    party = models.ForeignKey(
        Party, related_name='submissions', on_delete=models.PROTECT
    )
    # data might be received through physical mail; also, OS might decide to
    # make minor modifications on Party's submissions.
    filled_by_secretariat = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    created_by = models.ForeignKey(
        User, related_name='submissions_created', on_delete=models.PROTECT
    )
    last_edited_by = models.ForeignKey(
        User, related_name='submissions_last_edited', on_delete=models.PROTECT
    )

    # Per Obligation-ReportingPeriod-Party
    version = models.PositiveSmallIntegerField(default=1)

    # Persisted workflow class for this submission. We want this to be only set
    # at submission creation, so it will have no setter implementation.
    _workflow_class = models.CharField(
        max_length=32,
        choices=((w, w.capitalize()) for w in WORKFLOW_MAP.keys()),
        default='empty',
        db_column='workflow_class'
    )
    # States will be accessed through properties to enable custom logic
    # on state transitions.
    # We will impose no restriction on state name choices, as there is no
    # way of knowing them before runtime. Instead, the associated workflow
    # object (`self.workflow`) will be responsible for sane transitions.
    _current_state = models.CharField(
        max_length=64, null=True, blank=True, db_column='current_state'
    )
    # We need previous_state for un-recalling submissions
    _previous_state = models.CharField(
        max_length=64, null=True, blank=True, db_column='previous_state'
    )

    flag_provisional = models.BooleanField(default=False)
    flag_valid = models.NullBooleanField(default=None)
    flag_superseded = models.BooleanField(default=False)

    submitted_via = models.CharField(
        max_length=32,
        choices=((s.value, s.name) for s in SubmissionMethods)
    )

    # We want these to be able to be empty in forms
    remarks_party = models.CharField(max_length=512, blank=True)
    remarks_secretariat = models.CharField(max_length=512, blank=True)

    # Needed to track state changes and help with custom logic
    tracker = FieldTracker()

    @property
    def workflow_class(self):
        """Just a getter so we can access the class"""
        return self._workflow_class

    @property
    def workflow(self):
        """
        Creates workflow instance and set last *persisted* state on it
        """
        wf = self.WORKFLOW_MAP[self._workflow_class](model_instance=self)
        state = self.tracker.previous('_current_state') \
            if self.tracker.has_changed('_current_state') \
            else self.current_state
        wf.state = state or wf.state.workflow.initial_state
        return wf

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
            submission=self,
            transition=transition_name,
            from_state=self._previous_state,
            to_state=self._current_state,
        )
        self.save()

    @property
    def previous_state(self):
        """
        Previous state will only be changed indirectly when changing
        current_state; only a getter is needed.
        """
        return self._previous_state

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

        It automatically persists the previous and new states, by saving the
        entire instance!

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
            submission=self,
            transition=trans_name,
            from_state=self._previous_state,
            to_state=self._current_state,
        )
        self.save()

    def __str__(self):
        return f'{self.party.name} report on {self.obligation.name} ' \
               f'for {self.reporting_period.name} - version {self.version}'

    class Meta:
        # TODO: this constraint may not be true in the corner case of
        # obligations where reporting is done per-case (e.g. transfers).
        # It may happen that several transfers take place in the same
        # reporting period - this means that the constraint should be checked
        # using custom logic on save() rather than enforced here. Investigate!
        unique_together = (
            'party', 'reporting_period', 'obligation', 'version'
        )

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Auto-increment submission version if saving for a
        # party-obligation-reporting_period combo which already has submissions.
        # select_for_update() is used to lock the rows and ensure proper
        # concurrency.
        submissions = Submission.objects.select_for_update().filter(
            party=self.party,
            reporting_period=self.reporting_period,
            obligation=self.obligation
        )
        if submissions:
            self.version = submissions.latest('version').version + 1

        # TODO: this is not such a nice verification of first save
        # On first save we need to instantiate the submission's workflow
        if not self.pk or kwargs.get('force_insert', False):
            # TODO: get the proper workflow based on obligation and context
            # (e.g. fast-tracked secretariat submissions).
            # For now we will naively instantiate all submissions with
            # the default article 7 workflow.
            self._workflow_class = 'default'
            self._current_state = \
                self.workflow.state.workflow.initial_state.name

        return super().save(*args, **kwargs)


class TransitionEvent(models.Model):
    """
    Generic transition events in a submission's life cycle.
    """
    submission = models.ForeignKey(
        Submission, related_name='transition_events' ,on_delete=models.PROTECT
    )

    timestamp = models.DateTimeField(auto_now_add=True, editable=False)

    transition = models.CharField(max_length=60)
    from_state = models.CharField(max_length=60)
    to_state = models.CharField(max_length=60)
    triggered_by = models.ForeignKey(
        User, related_name='transitions_triggered', on_delete=models.PROTECT
    )
    extra = JSONField(encoder=DjangoJSONEncoder, null=True)

    class Meta:
        verbose_name = 'workflow event'
        unique_together = ('timestamp', 'submission', 'from_state', 'to_state')
