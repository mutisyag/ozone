import enum

__all__ = [
    'Reports'
]


@enum.unique
class Reports(enum.Enum):
    """
    Enum for describing different types of reports.
    """
    PRODCONS = 'prodcons'

    @staticmethod
    def items():
        return {e.name: e.value for e in Reports}
