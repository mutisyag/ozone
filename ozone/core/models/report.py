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
    def args(has_party_param=False, has_period_param=False):
        return {
            'has_party_param': has_party_param,
            'has_period_param': has_period_param
        }

    @staticmethod
    def prodcons_args():
        return Reports.args(has_party_param=True, has_period_param=True)

    @staticmethod
    def items():
        return [
            {**{'name': e.value}, **getattr(Reports, e.value + "_args")()}
            for e in Reports
        ]
