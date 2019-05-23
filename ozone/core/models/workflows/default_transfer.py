from django.utils.translation import gettext_lazy as _

import xworkflows

from .base import BaseWorkflow


class DefaultTransferWorkflowStateDescription(xworkflows.Workflow):
    """
    These are the default submission states and transitions
    for Article 7 reporting.
    """
    states = (
        ('data_entry', 'Data Entry'),
        ('submitted', 'Submitted'),
    )

    transitions = (
        ('submit', 'data_entry', 'submitted'),
    )

    initial_state = 'data_entry'


class DefaultTransferWorkflow(BaseWorkflow):

    """
    Implements custom transition logic for the default article 7 workflow.
    No states are truly final in this workflow.
    """
    final_states = ['submitted']
    editable_data_states = ['data_entry']
    incorrect_data_states = []

    state = DefaultTransferWorkflowStateDescription()

    @xworkflows.transition_check('submit')
    def check_submit(self):
        """
        Ensure that we only allow submitting submissions for there roles:
        * Party-write user from Party to which the submission refers to,
          only if the submission was started by the Party
        * Secretariat-write user, only if the submission was started by Secretariat

        This is also available for `recall` and `unrecall_to_*`
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
