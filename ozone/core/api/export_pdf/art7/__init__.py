from itertools import chain

from .section_info import export_info
from .section_impexp import export_imports
from .section_impexp import export_exports
from .section_production import export_production
from .section_destruction import export_destruction
from .section_nonparty import export_nonparty
from .section_emission import export_emission
from .section_labuses import export_labuses

from reportlab.platypus import PageBreak

__all__ = [
    'export_submissions',
]


def export_submissions(submissions):
    flowables = list()
    for idx, submission in enumerate(submissions):
        if idx > 0:
            flowables.append(PageBreak())
        flowables += list(chain(
            export_info(submission),
            export_imports(submission),
            export_exports(submission),
            export_production(submission),
            export_destruction(submission),
            export_nonparty(submission),
            export_emission(submission),
            export_labuses(submission),
        ))
    return flowables
