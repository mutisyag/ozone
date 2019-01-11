from itertools import chain

from .section_imports import export_imports
from .section_exports import export_exports
from .section_production import export_production


__all__ = [
    'export_submission',
    'export_imports',
    'export_exports',
    'export_production',
]


def export_submission(submission):
    return list(chain(
        export_imports(submission),
        export_exports(submission),
        export_production(submission),
    ))
