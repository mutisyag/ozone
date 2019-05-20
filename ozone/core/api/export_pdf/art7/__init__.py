from itertools import chain

from .section_info import export_info
from .section_impexp import export_imports
from .section_impexp import export_exports
from .section_production import export_production
from .section_destruction import export_destruction
from .section_nonparty import export_nonparty
from .section_emission import export_emission
from .others import get_prodcons_flowables

__all__ = [
    'export_submission',
    'export_prodcons',
]


def export_submission(submission):
    return list(chain(
        export_info(submission),
        export_imports(submission),
        export_exports(submission),
        export_production(submission),
        export_destruction(submission),
        export_nonparty(submission),
        export_emission(submission),
    ))


def export_prodcons(reporting_period, parties):
    return list(get_prodcons_flowables(reporting_period, parties))
