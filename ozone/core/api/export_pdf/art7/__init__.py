from itertools import chain

from .section_imports import export_imports


__all__ = [
    'export_imports',
]


def export_submission(submission):
    return list(chain(
        export_imports(submission),
    ))