from django.utils.translation import gettext_lazy as _

import xworkflows

from .base import BaseStateDescription, BaseWorkflow
from ...exceptions import TransitionFailed


__all__ = [
    'DefaultArticle7Workflow',
]


class DefaultArticle7WorkflowStateDescription(BaseStateDescription):
    """
    These are the default submission states and transitions
    for Article 7 reporting.
    """
    states = (
        ('data_entry', 'Data Entry'),
        ('submitted', 'Submitted'),
        ('recalled', 'Recalled'),
        ('processing', 'Processing'),
        ('finalized', 'Finalized'),
    )

    transitions = (
        ('submit', 'data_entry', 'submitted'),
        ('process', 'submitted', 'processing'),
        ('finalize', 'processing', 'finalized'),
        ('recall', ('submitted', 'processing', 'finalized'), 'recalled'),
        ('unrecall_to_submitted', 'recalled', 'submitted'),
        ('unrecall_to_processing', 'recalled', 'processing'),
        ('unrecall_to_finalized', 'recalled', 'finalized'),
    )

    initial_state = 'data_entry'


class DefaultArticle7Workflow(BaseWorkflow):

    """
    Implements custom transition logic for the default article 7 workflow.
    No states are truly final in this workflow.
    """
    final_states = []
    editable_data_states = ['data_entry']
    incorrect_data_states = ['recalled']

    state = DefaultArticle7WorkflowStateDescription()

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

    @xworkflows.transition_check('process')
    def check_process(self):
        return not self.user.is_read_only and self.user.is_secretariat

    @xworkflows.transition_check('recall')
    def check_recall(self):
        return (
            not self.user.is_read_only
            and self.is_secretariat_or_same_party_owner(self.model_instance)
        )

    @xworkflows.transition_check('unrecall_to_submitted')
    def check_unrecall_to_submitted(self):
        """
        Ensure that we only allow un-recalling submissions back to their
        initial state.
        """
        return (
            not self.user.is_read_only
            and self.is_secretariat_or_same_party_owner(self.model_instance)
            and self.model_instance.previous_state == 'submitted'
        )

    @xworkflows.transition_check('unrecall_to_processing')
    def check_unrecall_to_processing(self):
        return (
            not self.user.is_read_only
            and self.is_secretariat_or_same_party_owner(self.model_instance)
            and self.model_instance.previous_state == 'processing'
        )

    @xworkflows.transition_check('unrecall_to_finalized')
    def check_unrecall_to_finalized(self):
        return (
            not self.user.is_read_only
            and self.is_secretariat_or_same_party_owner(self.model_instance)
            and self.model_instance.previous_state == 'finalized'
        )

    @xworkflows.transition_check('finalize')
    def check_finalize(self):
        return (
            not self.user.is_read_only
            and self.user.is_secretariat
        )

    @xworkflows.before_transition('finalize')
    def before_finalize(self, *args, **kwargs):
        """
        Called right before the transition is actually performed.
        Used to avoid checking flag_valid's sanity in check_finalize, as that
        would have always shown the transition as unavailable
        """
        if self.model_instance.flag_valid is None:
            raise TransitionFailed(
                _('Valid flag must be set before submission is finalized')
            )

    @xworkflows.before_transition('submit')
    def before_submit(self, *args, **kwargs):
        """
        Called right before the transition is actually performed.
        """
        # Validate imports and exports data (will raise a validation error
        # if data is not consistent).
        self.model_instance.check_imports_exports()

    @xworkflows.transition('submit')
    def submit(self):
        # Make submission current
        self.model_instance.make_current()
        # Set submitted_at flag
        if self.model_instance.is_submitted_at_automatically_filled(self.user):
            self.model_instance.set_submitted()
        # If substances in annex F have been reported, set the time at which
        # they were reported.
        self.model_instance.set_annex_f_reported()

    @xworkflows.transition('recall')
    def recall(self):
        # Make previous submission current, if available
        self.model_instance.make_previous_current()

    @xworkflows.transition('unrecall_to_submitted')
    def unrecall_to_submitted(self):
        self.model_instance.make_current()

    @xworkflows.transition('unrecall_to_processing')
    def unrecall_to_processing(self):
        self.model_instance.make_current()

    @xworkflows.transition('unrecall_to_finalized')
    def unrecall_to_finalized(self):
        self.model_instance.make_current()
