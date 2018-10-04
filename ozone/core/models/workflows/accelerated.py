import xworkflows

from .base import BaseStateMachine, BaseWorkflow


class AcceleratedArticle7WorkflowStateDescription(xworkflows.Workflow):
    """
    This one does not include the `submitted` or `processing` states.

    It is meant to be used by Secretariat when amending submissions.
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


class AcceleratedArticle7WorkflowStateMachine(BaseStateMachine):
    # No states are truly final in this workflow
    final_states = []
    editable_data_states = ['data_entry']

    state = AcceleratedArticle7WorkflowStateDescription()


class AcceleratedArticle7Workflow(BaseWorkflow):
    WORKFLOW_CLASS = AcceleratedArticle7WorkflowStateMachine
