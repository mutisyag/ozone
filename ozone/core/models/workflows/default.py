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


class DefaultArticle7Workflow(BaseWorkflow):
    WORKFLOW_CLASS = DefaultArticle7WorkflowStateMachine
