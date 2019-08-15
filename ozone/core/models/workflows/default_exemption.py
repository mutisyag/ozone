from django.utils.translation import gettext_lazy as _

import xworkflows

from .base import BaseWorkflow
from .emails import notify_workflow_transitioned
from ...exceptions import TransitionFailed


__all__ = [
    'DefaultExemptionWorkflow',
]


class DefaultExemptionWorkflowStateDescription(xworkflows.Workflow):
    """
    These are the default submission states and transitions
    for Exemption workflow.
    """
    states = (
        ('data_entry', 'Data Entry'),
        ('submitted', 'Submitted'),
        ('processing', 'Processing'),
        ('finalized', 'Finalized'),
    )

    transitions = (
        ('submit', 'data_entry', 'submitted'),
        ('process', ('data_entry', 'submitted'), 'processing'),
        ('finalize', 'processing', 'finalized'),
    )

    initial_state = 'data_entry'


class DefaultExemptionWorkflow(BaseWorkflow):
    """
    Implements custom transition logic for the default Exemption workflow.
    """

    final_states = ['finalized']
    editable_data_states = ['data_entry', 'submitted', 'processing']
    incorrect_data_states = []

    state = DefaultExemptionWorkflowStateDescription()

    @xworkflows.transition_check('submit')
    def check_submit(self):
        return (
            not self.user.is_read_only
            and self.is_secretariat_or_same_party_owner(self.model_instance)
        )

    @xworkflows.transition_check('process')
    def check_process(self):
        # Do not allow secretariat users to directly send party-filled
        # submissions from data_entry to processing.
        if self.in_initial_state:
            if not self.model_instance.filled_by_secretariat:
                return False
        return self.user.is_secretariat and not self.user.is_read_only

    @xworkflows.transition_check('finalize')
    def check_finalize(self):
        return self.user.is_secretariat and not self.user.is_read_only

    @xworkflows.before_transition('finalize')
    def before_finalize(self, *args, **kwargs):
        """
        Called right before the "finalize" transition is actually performed.
        Used to avoid checking approved_valid's sanity in `check_finalize`, as
        that would have always shown the transition as unavailable.
        """
        if (
            self.model_instance.has_set_approved_flag()
            and not self.model_instance.has_filled_approved_exemptions()
        ):
            raise TransitionFailed(
                _(
                    'An exemption cannot be marked as approved without any'
                    'actual approved substances.'
                )
            )

        if (
            self.model_instance.has_set_approved_flag() is False
            and self.model_instance.has_filled_approved_exemptions()
        ):
            raise TransitionFailed(
                _(
                    'An exemption cannot be marked as not approved while having'
                    'approved substances.'
                )
            )

    @xworkflows.transition('submit')
    def submit(self):
        if self.model_instance.is_submitted_at_automatically_filled(self.user):
            self.model_instance.set_submitted()

    @xworkflows.on_enter_state(*[s.name for s in state.states])
    def notify_by_email(self, *args, **kwargs):
        notify_workflow_transitioned(self)
