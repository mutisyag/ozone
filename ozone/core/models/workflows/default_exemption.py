import xworkflows

from .base import BaseWorkflow


class DefaultExemptionWorkflowStateDescription(xworkflows.Workflow):
    """
    These are the default submission states and transitions
    for Exemption workflow.
    """
    states = (
        ('data_entry', 'Data Entry'),
        ('submitted', 'Submitted'),
        ('nomination_filled', 'Nomination Filled'),
        ('finalized', 'Finalized'),
    )

    transitions = (
        ('submit', 'data_entry', 'submitted'),
        ('fill_nomination', 'submitted', 'nomination_filled'),
        ('finalize', 'nomination_filled', 'finalized'),
    )

    initial_state = 'data_entry'


class DefaultExemptionWorkflow(BaseWorkflow):
    """
    Implements custom transition logic for the default Exemption workflow.
    """

    final_states = ['finalized']
    editable_data_states = ['data_entry', 'submitted', 'nomination_filled']

    state = DefaultExemptionWorkflowStateDescription()

    @xworkflows.transition_check('submit')
    def check_submit(self):
        return (
            not self.user.is_read_only
            and self.is_secretariat_or_same_party_owner(self.model_instance)
        )

    @xworkflows.transition_check('fill_nomination')
    def check_fill_nomination(self):
        return (
            not self.user.is_read_only and self.user.is_secretariat
            and self.model_instance.has_filled_nominations()
        )

    @xworkflows.transition_check('finalize')
    def check_finalize(self):
        return (
            not self.user.is_read_only and self.user.is_secretariat
            and self.model_instance.has_filled_approved_exemptions()
            and self.model_instance.has_set_approved_flag()
        ) or (
            not self.user.is_read_only and self.user.is_secretariat
            and self.model_instance.has_set_approved_flag() is False
            and not self.model_instance.has_filled_approved_exemptions()
        )

    @xworkflows.transition('submit')
    def submit(self):
        if self.model_instance.is_submitted_at_automatically_filled(self.user):
            self.model_instance.set_submitted()

