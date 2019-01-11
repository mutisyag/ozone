from itertools import chain

from .section_imports import export_imports
from .section_exports import export_exports
from .section_production import export_production
from .section_destruction import export_destruction


__all__ = [
    'export_submission',
    'export_imports',
    'export_exports',
    'export_production',
    'export_destruction'
]


def export_submission(submission):
    return list(chain(
        export_imports(submission),
        export_exports(submission),
        export_production(submission),
        export_destruction(submission),
    ))
