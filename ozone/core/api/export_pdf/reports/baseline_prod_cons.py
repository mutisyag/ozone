from collections import defaultdict
from decimal import Decimal

from django.utils.translation import gettext_lazy as _
from reportlab.platypus import Paragraph
from reportlab.platypus import PageBreak

from ozone.core.models import Baseline
from ozone.core.models import Group
from ozone.core.models import Party
from ozone.core.models import PartyHistory
from ozone.core.models import ProdCons
from ozone.core.models import ReportingPeriod

from ..util import h2_style
from ..util import SINGLE_HEADER_TABLE_STYLES
from ..util import col_widths
from ..util import TableBuilder
from ..util import smb_l
from ..util import smb_r
from ..util import sm_r
from ..util import format_decimal
from ..util import Report

from .prodcons.data import ValueNormalizer
from .prodcons.data import ValueFormatter


relevant_groups = ['AI', 'AII', 'BI', 'BII', 'BIII', 'EI']


def reference_periods_a5(group):
    if group.group_id in ['AI', 'AII']:
        return ReportingPeriod.objects.filter(name__in=['1995', '1996', '1997'])

    if group.group_id in ['BI', 'BII', 'BIII']:
        return ReportingPeriod.objects.filter(name__in=['1998', '1999', '2000'])

    if group.group_id in ['EI']:
        return ReportingPeriod.objects.filter(name__in=['1995', '1996', '1997', '1998'])

    raise RuntimeError(f"Unknown group {group!r}")


class GenericGroupTable:

    def __init__(self, group, parties):
        self.parties = parties
        self.group = group
        self.periods = list(reference_periods_a5(group))
        self.history_map = self.get_history_map(parties, self.periods[-1])
        self.filler_columns = 4 - len(self.periods)
        self.builder = self.begin_table()
        self.prodcons_map = self.get_prodcons_map()
        self.baseline_map = self.get_baseline_map()
        self.normalize = ValueNormalizer()
        self.format = ValueFormatter()
        self.totals = defaultdict(Decimal)

    def get_history_map(self, parties, period):
        history_queryset = (
            PartyHistory.objects
            .filter(party__in=parties)
            .filter(reporting_period=period)
            .select_related('party')
        )
        return {h.party: h for h in history_queryset}

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
            baseline_type__name=self.baseline_type,
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
        header += ["Baseline", f"Per Capita {self.label}", "Population"]
        builder.add_row(header)

        return builder

    def render_party(self, party):
        row = [party.name]

        raw_values = {}
        for period in self.periods:
            prodcons_row = self.prodcons_map.get((party, period))
            if prodcons_row:
                raw_value = self.prodcons_value(prodcons_row)
                raw_values[period] = raw_value
            else:
                raw_value = None

            value = self.normalize.prodcons(raw_value, self.group)
            row.append(sm_r(self.format.prodcons(value)))

        row += [""] * self.filler_columns

        db_baseline = self.baseline_map.get(party)
        if db_baseline is None and not any(raw_values.values()):
            return

        for period in self.periods:
            self.totals[period] += raw_values[period]

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
        row.append(smb_r(self.format.per_capita(self.totals['baseline'], self.totals['population'])))
        row.append(smb_r(format_decimal(self.totals['population'])))

        return row

    def render(self):
        for party in self.parties:
            row = self.render_party(party)
            if row:
                self.builder.add_row(row)

        self.builder.add_row(self.render_totals())

        yield self.builder.done()


class ProductionGroupTable(GenericGroupTable):

    baseline_type = "A5Prod"
    label = "Production"

    def prodcons_value(self, row):
        return row.calculated_production


class ConsumptionGroupTable(GenericGroupTable):

    baseline_type = "A5Cons"
    label = "Consumption"

    def prodcons_value(self, row):
        return row.calculated_consumption

    def render(self):
        yield from super().render()

        if len(self.parties) > 20:
            yield PageBreak()


class ProdConsBaselineTable:

    def __init__(self, period, parties):
        self.period = period
        self.parties = parties
        self.group_ai = Group.objects.get(group_id='AI')
        self.group_ci = Group.objects.get(group_id='CI')
        self.builder = self.begin_table()
        self.prodcons_map = self.get_prodcons_map()
        self.baseline_map = self.get_baseline_map()
        self.normalize = ValueNormalizer()
        self.format = ValueFormatter()

    def begin_table(self):
        styles = list(SINGLE_HEADER_TABLE_STYLES)
        column_widths = col_widths([4, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5])
        builder = TableBuilder(styles, column_widths)

        header = [
            "Party Name",
            f"{self.period.name} {self.group_ai.group_id} Production",
            f"{self.period.name} {self.group_ci.group_id} Production",
            f"Baseline {self.group_ci.group_id} Production",
            f"{self.period.name} {self.group_ai.group_id} Consumption",
            f"{self.period.name} {self.group_ci.group_id} Consumption",
            f"Baseline {self.group_ci.group_id} Consumption",
        ]
        builder.add_row(header)

        return builder

    def get_prodcons_map(self):
        prodcons_queryset = ProdCons.objects.filter(
            reporting_period=self.period,
            party__in=self.parties,
            group__in=[self.group_ai, self.group_ci],
        )
        return {
            (pc.party, pc.group): pc
            for pc in prodcons_queryset
        }

    def get_baseline_map(self):
        baseline_queryset = Baseline.objects.filter(
            party__in=self.parties,
            group=self.group_ci,
            baseline_type__name__in=["NA5Prod", "NA5Cons"],
        )
        return {
            (b.party, b.baseline_type.name):
            b.baseline for b in baseline_queryset
        }

    def prodcons_txt(self, party, group, is_prod):
        row = self.prodcons_map.get((party, group))
        if row:
            if is_prod:
                value = row.calculated_production
            else:
                value = row.calculated_consumption
        else:
            value = None

        normalized = self.normalize.prodcons(value, group)
        return self.format.prodcons(normalized)

    def baseline_txt(self, party, group, is_prod):
        baseline_type = "NA5Prod" if is_prod else "NA5Cons"
        value = self.baseline_map.get((party, baseline_type))
        normalized = self.normalize.baseline(value, group, None)
        return self.format.baseline(normalized, None)

    def render(self):
        for party in self.parties:
            self.builder.add_row([
                f"{party.name}",

                sm_r(self.prodcons_txt(party, self.group_ai, True)),
                sm_r(self.prodcons_txt(party, self.group_ci, True)),
                sm_r(self.baseline_txt(party, self.group_ci, True)),

                sm_r(self.prodcons_txt(party, self.group_ai, False)),
                sm_r(self.prodcons_txt(party, self.group_ci, False)),
                sm_r(self.baseline_txt(party, self.group_ci, False)),
            ])
        return self.builder.done()


def filter_by_art5(parties, is_article5):
    histories = (
        PartyHistory.objects
        .filter(reporting_period=ReportingPeriod.get_current_period())
        .filter(is_article5=is_article5)
        .filter(party__in=set(parties))
    )
    return list(Party.objects.filter(history__in=histories))


class BaselineProdA5Report(Report):

    name = "baseline_prod_a5"
    has_party_param = True
    display_name = "Baseline production - Art5 parties"
    description = _("Select one or more parties, or leave blank for all")

    def get_flowables(self):
        for group in Group.objects.filter(group_id__in=relevant_groups):
            yield Paragraph(
                f"{group.group_id} ({group.description}) "
                f"Production Baseline Data for Article 5 Parties (ODP tonnes)",
                h2_style,
            )
            table = ProductionGroupTable(group, filter_by_art5(self.parties, True))
            yield from table.render()


class BaselineConsA5Report(Report):

    name = "baseline_cons_a5"
    has_party_param = True
    display_name = "Baseline consumption - Art5 parties"
    description = _("Select one or more parties, or leave blank for all")

    def get_flowables(self):
        for group in Group.objects.filter(group_id__in=relevant_groups):
            yield Paragraph(
                f"{group.group_id} ({group.description}) "
                f"Consumption Baseline Data for Article 5 Parties (ODP tonnes)",
                h2_style,
            )
            table = ConsumptionGroupTable(group, filter_by_art5(self.parties, True))
            yield from table.render()


class BaselineProdConsNA5Report(Report):

    name = "baseline_prodcons_na5"
    has_party_param = True
    display_name = "Baseline C/I production and consumption - Non-Art5 parties"
    description = _("Select one or more parties, or leave blank for all")

    def get_flowables(self):
        period = ReportingPeriod.objects.get(name="1989")
        yield Paragraph(
            f"{period.name} Production and Consumption "
            f"of CI substances for Non-Article 5 Parties",
            h2_style,
        )

        table = ProdConsBaselineTable(period, filter_by_art5(self.parties, False))
        yield table.render()
