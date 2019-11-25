from collections import defaultdict
from decimal import Decimal

from reportlab.platypus import Paragraph
from reportlab.platypus import PageBreak

from ozone.core.models import Baseline
from ozone.core.models import Group
from ozone.core.models import PartyHistory
from ozone.core.models import ProdCons
from ozone.core.models import ReportingPeriod
from ozone.core.models.utils import round_decimal_half_up

from ..util import h2_style
from ..util import SINGLE_HEADER_TABLE_STYLES
from ..util import col_widths
from ..util import TableBuilder
from ..util import smb_l
from ..util import smb_r
from ..util import sm_r
from ..util import format_decimal

from .prodcons.data import ValueNormalizer
from .prodcons.data import ValueFormatter


def reference_periods_a5(group):
    if group.group_id in ['AI', 'AII']:
        return ReportingPeriod.objects.filter(name__in=['1995', '1996', '1997'])

    if group.group_id in ['BI', 'BII', 'BIII']:
        return ReportingPeriod.objects.filter(name__in=['1998', '1999', '2000'])

    if group.group_id in ['EI']:
        return ReportingPeriod.objects.filter(name__in=['1995', '1996', '1997', '1998'])

    raise RuntimeError(f"Unknown group {group!r}")


class GroupTable:

    def __init__(self, group, histories):
        self.parties = [h.party for h in histories]
        self.history_map = {h.party: h for h in histories}
        self.group = group
        self.periods = reference_periods_a5(group)
        self.filler_columns = 4 - len(self.periods)
        self.builder = self.begin_table()
        self.prodcons_map = self.get_prodcons_map()
        self.baseline_map = self.get_baseline_map()
        self.normalize = ValueNormalizer()
        self.format = ValueFormatter()
        self.totals = defaultdict(Decimal)

    def get_prodcons_map(self):
        prodcons_queryset = ProdCons.objects.filter(
            reporting_period__in=self.periods,
            party__in=self.parties,
            group=self.group,
        )
        return {
            (pc.party, pc.reporting_period): pc
            for pc in prodcons_queryset
        }

    def get_baseline_map(self):
        baseline_queryset = Baseline.objects.filter(
            baseline_type__name="A5Cons",
            group=self.group,
            party__in=self.parties,
        )
        return {b.party: b.baseline for b in baseline_queryset}

    def begin_table(self):
        styles = list(SINGLE_HEADER_TABLE_STYLES)
        column_widths = col_widths([5, 1.5, 1.5, 1.5, 1.5, 1.5, 3, 1.5])
        builder = TableBuilder(styles, column_widths)

        header = ["Party Name"]
        header += [p.name for p in self.periods]
        header += [""] * self.filler_columns
        header += ["Baseline", "Per Capita Consumption", "Population"]
        builder.add_row(header)

        return builder

    def render_party(self, party):
        row = [party.name]

        for period in self.periods:
            prodcons_row = self.prodcons_map.get((party, period))
            if prodcons_row:
                cons = prodcons_row.calculated_consumption
                self.totals[period] += cons
            else:
                cons = None

            value = self.normalize.prodcons(cons, self.group)
            row.append(sm_r(self.format.prodcons(value)))

        row += [""] * self.filler_columns

        db_baseline = self.baseline_map.get(party)
        baseline = self.normalize.baseline(db_baseline, self.group, None)
        row.append(sm_r(self.format.baseline(baseline, None)))

        history = self.history_map[party]
        population = history.population
        row.append(sm_r(self.format.per_capita(baseline, population)))
        row.append(sm_r(format_decimal(population)))

        if isinstance(baseline, Decimal):
            self.totals['baseline'] += baseline
            self.totals['per_capita'] += baseline / population
            self.totals['population'] += population

        return row

    def render_totals(self):
        row = [smb_l(f"Sub-total for Annex {self.group.group_id}")]
        for period in self.periods:
            value = self.totals[period]
            row.append(smb_r(self.format.prodcons(value)))

        row += [""] * self.filler_columns

        row.append(smb_r(self.format.baseline(self.totals['baseline'], None)))
        row.append(smb_r(format_decimal(round_decimal_half_up(self.totals['per_capita'], 4))))
        row.append(smb_r(format_decimal(self.totals['population'])))

        return row

    def render(self):
        for party in self.parties:
            self.builder.add_row(self.render_party(party))

        self.builder.add_row(self.render_totals())

        yield self.builder.done()

        if len(self.parties) > 20:
            yield PageBreak()


def get_cons_a5_flowables(parties):
    histories = list(
        PartyHistory.objects
        .filter(reporting_period=ReportingPeriod.get_current_period())
        .filter(is_article5=True)
        .filter(party__in=parties)
        .select_related('party')
    )

    relevant_groups = ['AI', 'AII', 'BI', 'BII', 'BIII', 'EI']
    for group in Group.objects.filter(group_id__in=relevant_groups):
        yield Paragraph(
            f"{group.group_id} ({group.description}) "
            f"Consumption Baseline Data for Article 5 Parties (ODP tonnes)",
            h2_style,
        )
        table = GroupTable(group, histories)
        yield from table.render()

    # TODO grand total
