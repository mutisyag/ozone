from .prodcons import get_prodcons_flowables


__all__ = [
    'export_prodcons',
]


def export_prodcons(reporting_period, parties, submission=None):
    return list(get_prodcons_flowables(reporting_period, parties, submission))
