from django.utils.translation import gettext_lazy as _

import xworkflows

from .base import BaseWorkflow
from .emails import notify_workflow_transitioned
from ...exceptions import TransitionFailed


__all__ = [
    'AcceleratedExemptionWorkflow',
]


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
    incorrect_data_states = []

    state = AcceleratedExemptionWorkflowStateDescription()

    @xworkflows.transition_check('finalize')
    def check_finalize(self):
        return self.user.is_secretariat and not self.user.is_read_only

    @xworkflows.before_transition('finalize')
    def before_finalize(self, *args, **kwargs):
        """
        Called right before the "finalize" transition is actually performed.

        Here we don't need to check approved flag because it makes no sense for
        the OS to create a submission with no approved exemptions.
        """

        if not self.model_instance.is_emergency():
            raise TransitionFailed(
                _(
                    'An emergency exemption needs to have its emergency flag'
                    'set.'
                )
            )

        if not self.model_instance.has_filled_approved_exemptions():
            raise TransitionFailed(
                _(
                    'An emergency exemption should have at least one'
                    'approved substance.'
                )
            )

    @xworkflows.on_enter_state(*[s.name for s in state.states])
    def notify_by_email(self, *args, **kwargs):
        notify_workflow_transitioned(self)
