from reportlab.platypus import Paragraph
from reportlab.platypus import PageBreak

from ozone.core.models import Group
from ozone.core.models import PartyHistory
from ozone.core.models import ProdCons
from ozone.core.models import ReportingPeriod

from ..util import h2_style
from ..util import SINGLE_HEADER_TABLE_STYLES
from ..util import col_widths
from ..util import TableBuilder
from ..util import format_decimal

from .prodcons.data import ValueNormalizer
from .prodcons.data import ValueFormatter


def relevant_periods_a5(group):
    if group.group_id in ['AI', 'AII']:
        return ReportingPeriod.objects.filter(name__in=['1995', '1996', '1997'])

    if group.group_id in ['BI', 'BII', 'BIII']:
        return ReportingPeriod.objects.filter(name__in=['1998', '1999', '2000'])

    if group.group_id in ['EI']:
        return ReportingPeriod.objects.filter(name__in=['1995', '1996', '1997', '1998'])

    raise RuntimeError(f"Unknown group {group!r}")


class GroupTable:

    def __init__(self, group, parties):
        self.group = group
        self.periods = relevant_periods_a5(group)
        self.filler_columns = 4 - len(self.periods)
        self.builder = self.begin_table()
        self.parties = parties
        self.prodcons_map = self.get_prodcons_map()
        self.normalize = ValueNormalizer()
        self.format = ValueFormatter()

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

    def begin_table(self):
        styles = list(SINGLE_HEADER_TABLE_STYLES)
        column_widths = col_widths([5, 1.5, 1.5, 1.5, 1.5, 2, 2, 2])
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
            else:
                cons = None

            value = self.normalize.prodcons(cons, self.group)
            row.append(self.format.prodcons(value))

        row += [""] * self.filler_columns

        return row

    def render(self):
        for party in self.parties:
            self.builder.add_row(self.render_party(party))
        yield self.builder.done()

        if len(self.parties) > 20:
            yield PageBreak()


def get_cons_a5_flowables(parties):
    current_period = ReportingPeriod.get_current_period()
    current_art5_histories = (
        PartyHistory.objects
        .filter(reporting_period=current_period)
        .filter(is_article5=True)
    )
    art5_parties = list(parties.filter(history__in=current_art5_histories))

    relevant_groups = ['AI', 'AII', 'BI', 'BII', 'BIII', 'EI']
    for group in Group.objects.filter(group_id__in=relevant_groups):
        yield Paragraph(f"{group}", h2_style)
        table = GroupTable(group, art5_parties)
        yield from table.render()
