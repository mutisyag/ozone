import xworkflows

from django.db import models


class BaseStateDescription(xworkflows.Workflow):
    """
    Placeholder class
    """
    states = ()
    transitions = ()
    initial_state = None


class BaseWorkflow(xworkflows.WorkflowEnabled):
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
        # We need this to add a back-reference to the
        # `Submission` model instance using this object.
        self.model_instance = model_instance
        super().__init__()

    @property
    def finished(self):
        return self.state in self.final_states

    @property
    def data_changes_allowed(self):
        return self.state in self.editable_data_states
