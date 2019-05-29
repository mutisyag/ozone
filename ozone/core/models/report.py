import enum

from django.utils.translation import gettext_lazy as _


__all__ = ['Reports']


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
    def prodcons_info():
        return {
            **Reports.args(has_party_param=True, has_period_param=True),
            **{
                "display_name": "Calculated production and consumption",
                "description": _(
                    "To compare the production and consumption of one year "
                    "with the baseline period, select only one year and one or "
                    "more parties. You can also select one party and two "
                    "reporting periods for comparing to each other."
                )
            },
        }

    @staticmethod
    def items():
        return [
            {**{'name': e.value}, **getattr(Reports, e.value + "_info")()}
            for e in Reports
        ]
