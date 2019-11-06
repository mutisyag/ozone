import enum

from django.utils.translation import gettext_lazy as _


__all__ = ['Reports']


@enum.unique
class Reports(enum.Enum):
    """
    Enum for describing different types of reports.
    """

    ART7_RAW = 'art7_raw'
    BASELINE_HFC_RAW = 'baseline_hfc_raw'
    PRODCONS = 'prodcons'
    RAF = 'raf'
    IMPEXP_NEW_REC = 'impexp_new_rec'
    HFC_BASELINE = 'hfc_baseline'

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
    def baseline_hfc_raw_info():
        return {
            **Reports.args(has_party_param=True),
            **{
                "display_name": "Baseline HFC raw data",
                "description": _(
                    "Select one or more parties"
                )
            },
        }

    @staticmethod
    def raf_info():
        return {
            **Reports.args(has_party_param=True, has_period_param=True),
            **{
                "display_name": "Reporting accounting framework essential and critical uses",
                "description": _(
                    "Select one or more parties and one or more reporting periods"
                )
            },
        }

    @staticmethod
    def impexp_new_rec_info():
        return {
            **Reports.args(has_party_param=True, has_period_param=True),
            **{
                "display_name": "Import and export of new and recovered substances",
                "description": _(
                    "Select one or more parties and one reporting period"
                )
            },
        }

    @staticmethod
    def hfc_baseline_info():
        return {
            **Reports.args(has_party_param=True),
            **{
                "display_name": "HFC baseline",
                "description": _(
                    "Select one or more parties and one reporting period"
                )
            },
        }

    @staticmethod
    def items():
        return [
            {**{'name': e.value}, **getattr(Reports, e.value + "_info")()}
            for e in Reports
        ]
