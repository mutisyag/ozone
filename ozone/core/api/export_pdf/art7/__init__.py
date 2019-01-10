from itertools import chain

from .section_imports import export_imports
from .section_production import export_production


__all__ = [
    'export_submission',
    'export_imports',
    'export_production',
]


def export_submission(submission):
    return list(chain(
        export_imports(submission),
        export_production(submission),
    ))
