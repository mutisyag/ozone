from collections import defaultdict

from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph

from ozone.core.models import Group
from ozone.core.models import Obligation
from ozone.core.models import ObligationTypes
from ozone.core.models import Party
from ozone.core.models import PartyHistory
from ozone.core.models import ProdCons
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
    ('ALIGN', (1, 2), (-1, -1), 'RIGHT'),
)

class ProdImpExpTable:

    def __init__(self, period):
        self.period = period

        self.all_groups = list(Group.objects.all())
        histories = PartyHistory.objects.filter(reporting_period=period)
        self.history_map = {h.party: h for h in histories}
        self.prodcons_map = self.get_prodcons_map()
        self.parties = Party.get_main_parties()
        art7 = Obligation.objects.get(_obligation_type=ObligationTypes.ART7.value)
        self.submission_map = Submission.latest_submitted_for_parties(art7, self.period, self.parties)

        self.format = data.ValueFormatter()
        self.builder = self.begin_table()

    def get_prodcons_map(self):
        rv = defaultdict(defaultdict)

        for row in ProdCons.objects.filter(reporting_period=self.period).iterator():
            if row.group in rv[row.party]:
                raise RuntimeError(f"duplicate wtf: {row.pk} {row}")
            rv[row.party][row.group] = row

        return dict(rv)

    def get_baselines(self, party):
        history = self.history_map[party]
        assert not history.is_article5
        return (0, 0)

    def begin_table(self):
        styles = list(DOUBLE_HEADER_TABLE_STYLES + TABLE_CUSTOM_STYLES)
        column_widths = col_widths([6, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5])
        builder = TableBuilder(styles, column_widths)
        builder.add_row([
            "",
            "PRODUCTION", "", "",
            "IMPORTS", "", "",
            "EXPORTS", "", "",
        ])
        builder.add_row([
            "",
            self.period.name, "Base", "% Chng",
            self.period.name, "Base", "% Chng",
            self.period.name, "Base", "% Chng",
        ])
        return builder

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

    def format_comparison(self, value, baseline):
        return [
            self.format.prodcons(value),
            self.format.baseline(baseline, value),
            self.format.change(value, baseline),
        ]

    def render_party(self, party):
        submission = self.submission_map.get(party)
        if not submission:
            return

        history = self.history_map[party]
        date_reported = get_date_of_reporting_str(submission)
        heading = self.party_heading(party, history, date_reported)
        self.builder.add_heading(heading)

        for group in self.all_groups:
            prodcons = self.prodcons_map[party].get(group)
            if not prodcons:
                continue

            value_prod = prodcons.calculated_production
            value_import = prodcons.import_new
            value_export = prodcons.export_new

            baseline_prod = prodcons.baseline_prod
            (baseline_import, baseline_export) = self.get_baselines(party)

            row = [group.name]
            row += self.format_comparison(value_prod, baseline_prod)
            row += self.format_comparison(value_import, baseline_import)
            row += self.format_comparison(value_export, baseline_export)

            self.builder.add_row(row)

    def render_parties(self):
        for party in self.parties:
            self.render_party(party)

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
