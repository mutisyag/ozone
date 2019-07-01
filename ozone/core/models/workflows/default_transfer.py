import xworkflows

from .base import BaseWorkflow
from .emails import notify_workflow_transitioned


__all__ = [
    'DefaultTransferWorkflow',
]


class DefaultTransferWorkflowStateDescription(xworkflows.Workflow):
    """
    These are the default submission states and transitions
    for Transfers reporting.
    """
    states = (
        ('data_entry', 'Data Entry'),
        ('submitted', 'Submitted'),
        ('finalized', 'Finalized'),
    )

    transitions = (
        ('submit', 'data_entry', 'submitted'),
        ('finalize', 'submitted', 'finalized'),
    )

    initial_state = 'data_entry'


class DefaultTransferWorkflow(BaseWorkflow):

    """
    Implements custom transition logic for the default transfer workflow.
    """
    final_states = ['finalized']
    editable_data_states = ['data_entry']
    incorrect_data_states = []

    state = DefaultTransferWorkflowStateDescription()

    @xworkflows.transition_check('submit')
    def check_submit(self):
        """
        Ensure that we only allow submitting submissions for there roles:
        * Party-write user from Party to which the submission refers to,
          only if the submission was started by the Party
        * Secretariat-write user, only if the submission was started by
          Secretariat
        """
        return (
            not self.user.is_read_only
            and self.is_secretariat_or_same_party_owner(self.model_instance)
            and self.model_instance.is_submittable()
        )

    @xworkflows.transition('submit')
    def submit(self):
        # Set submitted_at flag
        if self.model_instance.is_submitted_at_automatically_filled(self.user):
            self.model_instance.set_submitted()

    @xworkflows.transition_check('finalize')
    def check_finalize(self):
        """
        Ensure that only secretariat-edit users can finalize submissions
        """
        return not self.user.is_read_only and self.user.is_secretariat

    @xworkflows.on_enter_state(*[s.name for s in state.states])
    def notify_by_email(self, *args, **kwargs):
        notify_workflow_transitioned(self)
