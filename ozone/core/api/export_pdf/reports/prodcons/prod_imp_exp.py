from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph

from ozone.core.models import Obligation
from ozone.core.models import ObligationTypes
from ozone.core.models import Party
from ozone.core.models import PartyHistory
from ozone.core.models import Submission

from ozone.core.api.export_pdf.util import h2_style
from ozone.core.api.export_pdf.util import DOUBLE_HEADER_TABLE_STYLES
from ozone.core.api.export_pdf.util import col_widths
from ozone.core.api.export_pdf.util import TableBuilder
from ozone.core.api.export_pdf.util import get_date_of_reporting_str
from ozone.core.api.export_pdf.util import format_decimal

from . import data
from . import render


TABLE_CUSTOM_STYLES = (
    ('SPAN', (0, 0), (0, 1)),  # blank
    ('SPAN', (1, 0), (3, 0)),  # production
    ('SPAN', (4, 0), (6, 0)),  # imports
    ('SPAN', (7, 0), (9, 0)),  # exports
    # ('ALIGN', (1, 2), (-1, -1), 'RIGHT'),
)

class ProdImpExpTable:

    def __init__(self, period):
        self.period = period
        styles = list(DOUBLE_HEADER_TABLE_STYLES + TABLE_CUSTOM_STYLES)
        column_widths = col_widths([6, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5])
        self.builder = TableBuilder(styles, column_widths)
        self.builder.add_row([
            "",
            "PRODUCTION", "", "",
            "IMPORTS", "", "",
            "EXPORTS", "", "",
        ])
        self.builder.add_row([
            "",
            self.period.name, "Base", "% Chng",
            self.period.name, "Base", "% Chng",
            self.period.name, "Base", "% Chng",
        ])

    def party_heading(self, party, history, date_reported):
        badges = []

        if history.is_article5:
            badges.append("A5")
        else:
            badges.append("Non-A5")

        if history.is_ceit:
            badges.append("CEIT")

        if history.is_eu_member:
            badges.append("EU")

        return (f"{party.name}  (Date Reported: {date_reported}) - {' '.join(badges)}  "
                f"(Population: {format_decimal(history.population)})")

    def render_parties(self):
        parties = Party.get_main_parties()
        art7 = Obligation.objects.get(_obligation_type=ObligationTypes.ART7.value)
        submission_map = Submission.latest_submitted_for_parties(art7, self.period, parties)
        histories = PartyHistory.objects.filter(reporting_period=self.period)
        history_map = {h.party: h for h in histories}

        for party in parties:
            submission = submission_map.get(party)
            if not submission:
                continue

            history = history_map[party]
            date_reported = get_date_of_reporting_str(submission)
            heading = self.party_heading(party, history, date_reported)
            self.builder.add_heading(heading)

    def done(self):
        return self.builder.done()


def render_header(period):
    title = (
        f"Production, Import and Export of ODSs - "
        f"Comparison of {period.name} with Base (ODP Tons)"
    )
    return Paragraph(title, style=h2_style)


def get_prod_imp_exp_flowables(periods):
    all_groups = data.get_all_groups()
    groups_description = list(render.get_groups_description(all_groups))

    for period in periods:
        yield render_header(period)
        yield from groups_description

        table = ProdImpExpTable(period)
        table.render_parties()
        yield table.done()

        yield PageBreak()
