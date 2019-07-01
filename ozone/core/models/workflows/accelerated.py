import xworkflows

from .base import BaseWorkflow


__all__ = [
    'AcceleratedArticle7Workflow',
]


class AcceleratedArticle7WorkflowStateDescription(xworkflows.Workflow):
    """
    These are the "accelerated" submission states and transitions
    for Article 7 reporting. They do not include the `submitted` or
    `processing` states.

    This workflow is meant to be used by Secretariat when amending submissions.
    """

    states = (
        ('data_entry', 'Data Entry'),
        ('recalled', 'Recalled'),
        ('finalized', 'Finalized'),
    )

    transitions = (
        ('finalize', 'data_entry', 'finalized'),
        ('recall', 'finalized', 'recalled'),
        ('unrecall', 'recalled', 'finalized')
    )

    initial_state = 'data_entry'


class AcceleratedArticle7Workflow(BaseWorkflow):

    # No states are truly final in this workflow
    final_states = []
    editable_data_states = ['data_entry']
    incorrect_data_states = ['recalled']

    state = AcceleratedArticle7WorkflowStateDescription()

    @xworkflows.transition_check('finalize')
    def check_finalize(self):
        return (
            self.user.is_secretariat
            and not self.user.is_read_only
            and self.model_instance.is_submittable()
        )

    @xworkflows.transition_check('recall')
    def check_recall(self):
        return not self.user.is_read_only and self.user.is_secretariat

    @xworkflows.transition_check('unrecall')
    def check_unrecall(self):
        return not self.user.is_read_only and self.user.is_secretariat

    @xworkflows.transition('finalize')
    def finalize(self):
        self.model_instance.make_current()
        if self.model_instance.is_submitted_at_automatically_filled(self.user):
            self.model_instance.set_submitted()

    @xworkflows.transition('recall')
    def recall(self):
        # Make previous submission current, if available
        self.model_instance.make_previous_current()

    @xworkflows.transition('unrecall')
    def unrecall(self):
        self.model_instance.make_current()

    @xworkflows.on_enter_state(*[s.name for s in state.states])
    def notify_by_email(self, *args, **kwargs):
        notify_workflow_transitioned(self)
