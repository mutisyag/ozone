import xworkflows

from .base import BaseStateMachine, BaseWorkflow


class DefaultArticle7WorkflowStateDescription(xworkflows.Workflow):
    """
    This is the default submission workflow for Article 7 reporting
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


class DefaultArticle7WorkflowStateMachine(BaseStateMachine):
    # No states are truly final in this workflow
    final_states = []
    editable_data_states = ['data_entry']

    state = DefaultArticle7WorkflowStateDescription()

    @xworkflows.transition_check('unrecall_to_submitted')
    def check_unrecall_to_submitted(self):
        """
        Ensure that we only allow un-recalling submissions back to their
        initial state.
        """
        return self.model_instance.previous_state == 'submitted'

    @xworkflows.transition_check('unrecall_to_processing')
    def check_unrecall_to_processing(self):
        return self.model_instance.previous_state == 'processing'

    @xworkflows.transition_check('unrecall_to_finalized')
    def check_unrecall_to_finalized(self):
        return self.model_instance.previous_state == 'finalized'

    @xworkflows.transition_check('finalize')
    def check_finalize(self):
        return self.model_instance.submission.flag_valid is not None


class DefaultArticle7Workflow(BaseWorkflow):
    WORKFLOW_CLASS = DefaultArticle7WorkflowStateMachine
