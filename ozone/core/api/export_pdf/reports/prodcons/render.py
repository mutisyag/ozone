from django.utils.translation import gettext_lazy as _
from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph

from ozone.core.api.export_pdf.util import (
    h1_style, h2_style, sm_no_spacing_style,
    sm_l,
)

def get_header(party_name):
    return (
        Paragraph(party_name.upper(), style=h1_style),
        Paragraph("Production and Consumption - Comparison with Base Year", style=h2_style),
    )


def get_summary_report_header(period, name):
    yield Paragraph(
        _("Production and Consumption of ODSs - Comparison of {period} with")
        .format(period=period.name),
        style=h1_style,
    )
    yield Paragraph(
        _("Baseline: {name} (ODP/CO2-eq Tonnes)").format(name=name),
        style=h1_style,
    )


def get_groups_description(all_groups):
    for group in all_groups:
        yield Paragraph(
            f"{group.group_id} - {group.name_alt} "
            f"{group.description}. {group.description_alt}",
            sm_no_spacing_style
        )

    yield Paragraph("", style=h1_style)


def get_footer():
    yield sm_l(_(
        """* Population in thousands <br/>
        ** Consumption and Production numbers are rounded to a uniform number of decimal places. <br/><br/>
        - = Data Not Reported and Party has no Obligation to have Reported that data at this time. <br/>
        N.R. = Data Not Reported but Party is required to have reported |
        AFR = Africa |
        ASIA = Asia |
        EEUR = Eastern Europe |
        LAC = Latin America & the Caribbean |
        WEUR = Western Europe & others |
        A5 = Article 5 Party |
        NA5 = Non-Article 5 Party"""
    ))
    yield PageBreak()
