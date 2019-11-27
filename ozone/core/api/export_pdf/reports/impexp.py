from collections import defaultdict

from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph

from ozone.core.models import Article7Import
from ozone.core.models import Article7Export
from ozone.core.models import Group
from ozone.core.models import Obligation
from ozone.core.models import ObligationTypes
from ozone.core.models import Party
from ozone.core.models import PartyHistory
from ozone.core.models import Submission
from ozone.core.models import Substance

from ..util import h1_style
from ..util import sm_r
from ..util import SINGLE_HEADER_TABLE_STYLES
from ..util import col_widths
from ..util import TableBuilder
from ..util import format_decimal
from ..util import bold_centered_paragraph_style


class RecoveredImportExportTable:

    def __init__(self, period):
        self.period = period
        self.get_data()

    def get_data(self):
        main_parties = Party.get_main_parties()
        art7 = Obligation.objects.get(_obligation_type=ObligationTypes.ART7.value)
        self.submissions = Submission.latest_submitted_for_parties(
            art7,
            self.period,
            main_parties,
        )

        self.group_map = {g.pk: g for g in Group.objects.all()}

        imports_queryset = (
            Article7Import.objects
            .filter(submission__in=self.submissions.values())
            .filter(blend_item_id__isnull=True)
            .prefetch_related('substance', 'blend')
        )
        self.imports_by_submission = defaultdict(list)
        for i in imports_queryset:
            self.imports_by_submission[i.submission_id].append(i)

        exports_queryset = (
            Article7Export.objects
            .filter(submission__in=self.submissions.values())
            .filter(blend_item_id__isnull=True)
            .prefetch_related('substance', 'blend')
        )
        self.exports_by_submission = defaultdict(list)
        for i in exports_queryset:
            self.exports_by_submission[i.submission_id].append(i)

    def get_parties(self, is_article5):
        histories = (
            PartyHistory.objects
            .filter(reporting_period=self.period)
            .filter(is_article5=is_article5)
        )
        return Party.objects.filter(history__in=histories)

    def begin_table(self):
        styles = list(SINGLE_HEADER_TABLE_STYLES)
        column_widths = col_widths([10, 2, 3, 3])
        builder = TableBuilder(styles, column_widths)

        builder.add_row([
            "Substance Name",
            "Annex / Group",
            "Recovered Import",
            "Recovered Export",
        ])

        return builder

    def format_value(self, value):
        if value is None:
            return ""
        return format_decimal(value)

    def render_party(self, party):
        submission = self.submissions.get(party)
        if not submission:
            return

        rows_by_substance = defaultdict(dict)

        for i in self.imports_by_submission[submission.pk]:
            value = i.quantity_total_recovered
            if value:
                substance = i.substance or i.blend
                rows_by_substance[substance]['recovered_import'] = value

        for i in self.exports_by_submission[submission.pk]:
            value = i.quantity_total_recovered
            if value:
                substance = i.substance or i.blend
                rows_by_substance[substance]['recovered_export'] = value

        if not rows_by_substance:
            return

        self.builder.add_heading(party.name)

        for substance in sorted(rows_by_substance, key=lambda s: s.sort_order):
            row = rows_by_substance[substance]

            if isinstance(substance, Substance):
                substance_txt = str(substance)
                group_txt = self.group_map[substance.group_id].group_id
            else:
                substance_txt = f"{substance} ({substance.composition})"
                group_txt = ""

            self.builder.add_row([
                substance_txt,
                group_txt,
                sm_r(self.format_value(row.get('recovered_import'))),
                sm_r(self.format_value(row.get('recovered_export'))),
            ])

    def render(self):
        self.builder = self.begin_table()

        self.builder.add_heading("Article 5 parties", style=bold_centered_paragraph_style)
        for party in self.get_parties(is_article5=True):
            self.render_party(party)

        self.builder.add_heading("Non-Article 5 parties", style=bold_centered_paragraph_style)
        for party in self.get_parties(is_article5=False):
            self.render_party(party)

        return self.builder.done()


def get_rec_subst_flowables(periods):
    for period in periods:
        yield Paragraph(
            f"Recovered ODSs Imported and Exported by "
            f"the Parties in {period.name} (Tonnes)",
            h1_style,
        )
        table = RecoveredImportExportTable(period)
        yield table.render()
        yield PageBreak()
