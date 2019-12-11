from django.utils.translation import gettext_lazy as _
from reportlab.platypus import Paragraph, Table

from ozone.core.models import Baseline
from ozone.core.models import ProdCons
from ozone.core.models import ReportingPeriod
from ozone.core.models.utils import round_decimal_half_up
from ozone.core.calculated.baselines import BaselineCalculator
from ..util import (
    h1_style, h2_style, sm_no_spacing_style,
    col_widths,
    SINGLE_HEADER_TABLE_STYLES,
    Report,
)

NOT_REPORTED = object()


def blank(value):
    return "-"


def decimal_value(value):
    if value is None:
        return '-'
    elif value is NOT_REPORTED:
        return 'N.R.'
    else:
        return f"{round_decimal_half_up(value):,}"


class ReportTable:
    header = [
        _('Annex'),
        _('Annex Group Name'),
        _('Period'),
        _('Production'),
        _('Consumption'),
    ]

    table_style = SINGLE_HEADER_TABLE_STYLES + (
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
    )

    def __init__(self, calculator, current_period, party):
        self.calculator = calculator
        self.party = party
        current_history = party.history.get(reporting_period=current_period)

        self.group_ai = calculator.groups['AI']
        self.group_ci = calculator.groups['CI']
        self.group_f = calculator.groups['F']

        def period(name):
            return calculator.reporting_periods[name]

        def baseline_type(name):
            return calculator.baseline_types[name]

        if current_history.is_article5:
            self.baseline_type_prod = baseline_type('A5ProdGWP')
            self.baseline_type_cons = baseline_type('A5ConsGWP')
            self.cfc_groups = [self.group_ci]
            self.cfc_periods = ['2009', '2010']
            if current_history.is_group2():
                self.hfc_periods = [period(p) for p in ['2024', '2025', '2026']]
            else:
                self.hfc_periods = [period(p) for p in ['2020', '2021', '2022']]

        else:
            self.baseline_type_prod = baseline_type('NA5ProdGWP')
            self.baseline_type_cons = baseline_type('NA5ConsGWP')
            self.cfc_groups = [self.group_ai, self.group_ci]
            self.cfc_periods = ['1989']
            self.hfc_periods = [period(p) for p in ['2011', '2012', '2013']]

        self.hfc_prodcons_map = {
            prodcons.reporting_period: prodcons
            for prodcons in ProdCons.objects.filter(
                party=self.party,
                group=self.group_f,
                reporting_period__in=self.hfc_periods,
            )
        }
        self.baseline_map = {
            (baseline.group, baseline.baseline_type): baseline.baseline
            for baseline in Baseline.objects.filter(
                party=self.party,
                group__in=[self.group_ci, self.group_f],
                baseline_type__in=[self.baseline_type_prod, self.baseline_type_cons],
            )
        }

        self.prod_value = blank if party.is_eu else decimal_value
        self.cons_value = blank if current_history.is_eu_member else decimal_value

    def prodcons_gwp_row(self, group, period_name):
        prod = self.calculator._prod_cons_gwp(self.party, group, period_name, 'PROD')
        cons = self.calculator._prod_cons_gwp(self.party, group, period_name, 'CONS')
        return [
            group.group_id,
            group.description,
            period_name,
            self.prod_value(prod),
            self.cons_value(cons),
        ]

    def baseline_row(self, group):
        return [
            group.group_id,
            group.description,
            'Baseline',
            self.prod_value(self.baseline_map.get((group, self.baseline_type_prod))),
            self.cons_value(self.baseline_map.get((group, self.baseline_type_cons))),
        ]

    def prodcons_hfc_row(self, period, prodcons):
        prod = prodcons.calculated_production if prodcons else NOT_REPORTED
        cons = prodcons.calculated_consumption if prodcons else NOT_REPORTED

        return [
            self.group_f.group_id,
            self.group_f.description,
            period.name,
            self.prod_value(prod),
            self.cons_value(cons),
        ]

    def rows(self):
        for period_name in self.cfc_periods:
            for group in self.cfc_groups:
                yield self.prodcons_gwp_row(group, period_name)
        yield self.baseline_row(self.group_ci)

        for period in self.hfc_periods:
            yield self.prodcons_hfc_row(period, self.hfc_prodcons_map.get(period))

        yield self.baseline_row(self.group_f)

    def table(self):
        rows = [self.header] + list(self.rows())

        return Table(
            rows,
            colWidths=col_widths([1.5, 7, 2.5, 4, 4]),
            style=self.table_style,
            hAlign='LEFT',
        )


def group_description(group):
    text = (
        f"{group.group_id} - {group.name_alt} "
        f"{group.description}. {group.description_alt}"
    )
    return Paragraph(text, sm_no_spacing_style)


class HFCBaselineReport(Report):

    name = "hfc_baseline"
    has_party_param = True
    display_name = "HFC baseline"
    description = _("Select one or more parties and one reporting period")

    def get_flowables(self):
        calculator = BaselineCalculator()
        current_period = ReportingPeriod.get_current_period()
        yield Paragraph(_("HFC Baseline data (in CO2-equivalent tonnes)"), h1_style)

        for group_id in ['CI', 'F']:
            yield group_description(calculator.groups[group_id])

        for party in self.parties:
            yield Paragraph(party.name.upper(), h2_style)
            yield ReportTable(calculator, current_period, party).table()
