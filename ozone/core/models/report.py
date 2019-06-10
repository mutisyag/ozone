import enum

from django.utils.translation import gettext_lazy as _


__all__ = ['Reports']


@enum.unique
class Reports(enum.Enum):
    """
    Enum for describing different types of reports.
    """

    ART7_RAW = 'art7_raw'
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
                "display_name": "Production and consumption - comparison with base year",
                "description": _(
                    "Select one or more parties and one or more reporting periods"
                )
            },
        }

    @staticmethod
    def art7_raw_info():
        return {
            **Reports.args(has_party_param=True, has_period_param=True),
            **{
                "display_name": "Raw data reported - Article 7",
                "description": _(
                    "Select one or more parties and one or more reporting periods"
                )
            },
        }

    @staticmethod
    def items():
        return [
            {**{'name': e.value}, **getattr(Reports, e.value + "_info")()}
            for e in Reports
        ]
