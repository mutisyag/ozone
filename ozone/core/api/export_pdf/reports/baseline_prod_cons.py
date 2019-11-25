from reportlab.platypus import Paragraph

from ozone.core.models import PartyHistory
from ozone.core.models import ReportingPeriod

from ..util import h1_style


def get_cons_a5_flowables(parties):
    current_period = ReportingPeriod.get_current_period()
    current_art5_histories = (
        PartyHistory.objects
        .filter(reporting_period=current_period)
        .filter(is_article5=True)
    )
    art5_parties = parties.filter(history__in=current_art5_histories)
    return [Paragraph(
        f'Article 5 baseline consumption: {len(art5_parties)} parties',
        h1_style,
    )]
