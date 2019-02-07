import xworkflows

from .base import BaseWorkflow


class AcceleratedExemptionWorkflowStateDescription(xworkflows.Workflow):
    """
    These are the submission states and transitions
    for the accelerated Exemption workflow.
    """

    states = (
        ('data_entry', 'Data Entry'),
        ('finalized', 'Finalized'),
    )

    transitions = (
        ('finalize', 'data_entry', 'finalized'),
    )

    initial_state = 'data_entry'


class AcceleratedExemptionWorkflow(BaseWorkflow):
    """
    Implements custom transition logic for the accelerated Exemption workflow.
    """

    final_states = ['finalized']
    editable_data_states = ['data_entry']

    state = AcceleratedExemptionWorkflowStateDescription()

    @xworkflows.transition_check('finalize')
    def check_finalize(self):
        """
        Here we don't need to check approved flag becasue it makes no sense for
        the OS to create a submission with no approved exemptions.
        """
        return (
            not self.user.is_read_only and self.user.is_secretariat
            and self.model_instance.has_filled_approved_exemptions()
            and self.model_instance.is_emergency()
        )

