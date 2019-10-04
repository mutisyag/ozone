import logging

from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from functools import lru_cache
from openpyxl import load_workbook
import collections

from ozone.core.models import (
    Party,
    PartyHistory,
    Submission,
    ReportingPeriod,
    Group,
    ProdCons,
    Transfer,
    BaselineType,
    Baseline,
)
from ozone.core.models.utils import (
    round_decimal_half_up,
    sum_decimals,
    float_to_decimal,
    float_to_decimal_zero_if_none,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = __doc__

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super().__init__(stdout=None, stderr=None, no_color=False)

        self.groups = {
            _group.group_id: _group
            for _group in Group.objects.all()
        }
        self.reporting_periods = {
            _period.name: _period
            for _period in ReportingPeriod.objects.all()
        }
        self.parties = {
            _party.abbr: _party
            for _party in Party.get_main_parties()
        }
        self.eu_member_states = [
            _party.abbr
            for _party in Party.get_eu_members()
        ]
        self.eu_member_states_1989 = [
            _party.abbr
            for _party in Party.get_eu_members_at(
                self.reporting_periods['1989']
            )
        ]

        def _new_eu_member_states_since(period_name):
            return [
                self.parties[_party]
                for _party in self.eu_member_states
                if _party not in [
                    _p.abbr
                    for _p in Party.get_eu_members_at(
                        self.reporting_periods[period_name]
                    )
                ]
            ]
        self.new_eu_member_states_since = {
            _period: _new_eu_member_states_since(_period)
            for _period in ('1989', '2009', '2010')
        }

    def add_arguments(self, parser):
        parser.add_argument(
            '--party',
            help="Party code, for limiting the calculation to a single party"
        )
        parser.add_argument(
            '--simulate',
            action='store_true',
            help="Don't store any change, only simulate"
        )
        parser.add_argument(
            '--test_file',
            help="Location of the tbl_prod_cons.xlsx file "
            "for checking computed values with legacy data"
        )

    def handle(self, *args, **options):
        stream = logging.StreamHandler()
        stream.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s'
        ))
        logger.addHandler(stream)
        logger.setLevel(logging.INFO)

        if int(options['verbosity']) > 1:
            logger.setLevel(logging.DEBUG)

        if options['party']:
            parties = (Party.objects.get(abbr=options['party']),)
        else:
            parties = Party.get_main_parties()

        if options['test_file']:
            results = self.load_legacy_data(options['test_file'])
            self.test_legacy_data(results)
        else:
            for party in parties:
                self.process_party(party, options)

    def load_legacy_data(self, filename):
        logger.debug('Loading Excel file....')
        wb = load_workbook(filename=filename)
        logger.debug('Processing data...')
        sheet = wb.active
        values = list(sheet.values)
        results = collections.defaultdict(list)
        headers = values[0]
        for row in values[1:]:
            row = dict(zip(headers, row))
            if not row["PeriodID"].startswith("Base"):
                continue
            pk = row["CntryID"], row["PeriodID"][4:], row["Anx"], row["Grp"]
            results[pk] = row
        return results

    def test_legacy_data(self, results):
        errors = list()
        for pk, row in results.items():
            # key = (CntryId, A5/NA5, Anx, Grp)
            party = self.parties[pk[0]]
            suffix = ''
            if not pk[3]:
                # this is GWP baseline for A/I, C/I or F
                group_name = (pk[2] + 'I') if pk[2] in ['A', 'C'] else pk[2]
                suffix = 'GWP'
            else:
                group_name = pk[2]+pk[3]
            group = self.groups[group_name]
            for kind in ('Prod', 'Cons'):
                baseline_type = pk[1] + kind + suffix
                computed = self.get_baseline(baseline_type, group, party)
                legacy = float_to_decimal(row["Calc" + kind])
                log_line = f"{pk} Calc{kind} computed={computed} legacy={legacy}"
                logger.debug(f"Checking {log_line}")
                if computed != legacy and not (
                    # Skip some known issues when computed is None for EU members
                    computed is None and party.abbr in self.eu_member_states and (
                        legacy == 0 or baseline_type in ('A5ConsGWP', 'NA5ConsGWP')
                    ) or
                    computed is None and party.abbr == 'EU' and (
                        baseline_type in ('A5ProdGWP, NA5ProdGWP')
                    )
                ):
                    logger.error(f"Failed for {log_line}")
                    errors.append(f"{log_line}")

            # check ProdArt5 vs BDN_NA5
            if (
                pk[1] == 'NA5' and
                suffix == '' and
                group.group_id in ('AI', 'AII', 'BI', 'E') and
                party.abbr != 'EU'
            ):
                computed = self.get_baseline('BDN_NA5', group, party)
                legacy = float_to_decimal_zero_if_none(row["ProdArt5"])
                log_line = f"{pk} ProdArt5 computed={computed} legacy={legacy}"
                logger.debug(f"Checking {log_line}")
                if computed != legacy and not (
                    computed is None and legacy == 0
                ):
                    logger.error(f"Failed for {log_line}")
                    errors.append(f"{log_line}")

        if errors:
            logger.error(f"Total errors: {len(errors)}")
            logger.error("\n".join(errors))
        else:
            logger.info("All checks passed. Good job!")

    def process_party(self, party, options):
        logger.info(f"Processing party {party.abbr} {party.name}")
        for group in self.groups.values():
            must_update_prodcons = False
            for baseline_type in BaselineType.objects.all():
                baseline = self.get_baseline(baseline_type.name, group, party)
                if baseline is not None:
                    logger.debug("Got {:10f} for {}/{}/{}".format(
                        baseline.normalize(),
                        party.abbr,
                        baseline_type.name,
                        group.group_id,
                    ))
                if options['simulate']:
                    continue

                has_changed = self._persist_baseline(baseline_type, group, party, baseline)
                if baseline_type.name in ('A5Prod', 'A5Cons', 'NA5Prod', 'NA5Cons'):
                    must_update_prodcons = must_update_prodcons or has_changed

            if must_update_prodcons:
                # invoke after all baseline types for this group are computed
                self._update_prodcons(group, party)

    def _persist_baseline(self, baseline_type, group, party, new_value):
        has_changed = False
        if new_value is None:
            count, _ = Baseline.objects.filter(
                party=party,
                group=group,
                baseline_type=baseline_type,
            ).delete()
            if count > 0:
                logger.info("Deleted previous baseline for {}/{}/{}".format(
                    party.abbr,
                    baseline_type.name,
                    group.group_id,
                ))
                has_changed = True
        else:
            # get_or_create insteadof update_or_create to log only real changes
            obj, _created = Baseline.objects.get_or_create(
                party=party,
                group=group,
                baseline_type=baseline_type,
            )
            if _created:
                logger.info("Creating new baseline for {}/{}/{} = {}".format(
                    party.abbr,
                    baseline_type.name,
                    group.group_id,
                    new_value,
                ))
            elif obj.baseline != new_value:
                has_changed = True
                logger.info("Updating baseline for {}/{}/{} from {} to {}".format(
                    party.abbr,
                    baseline_type.name,
                    group.group_id,
                    obj.baseline,
                    new_value,
                ))
            obj.baseline = new_value
            obj.save()
            return has_changed

    def _update_prodcons(self, group, party):
        qs = ProdCons.objects.filter(
            party=party,
            group=group,
        )
        for prodcons in qs.all():
            prodcons.populate_limits_and_baselines()
            prodcons.save()

    def get_baseline(self, baseline_type, group, party):
        func, periods = getattr(
            self, 'baseline_' + baseline_type
        )(group, party)
        return func(party, group, periods) if func else None

    @lru_cache(maxsize=128)
    def _get_prodcons(self, party, group, period_name):
        try:
            return ProdCons.objects.get(
                party=party,
                reporting_period__name=period_name,
                group=group,
            )
        except ProdCons.DoesNotExist:
            logger.warning("{} has not reported {} for {}".format(
                party.name,
                group.group_id,
                period_name
            ))
            return None

    def _get_bdn_transfer(self, party, group, period_name):
        transfers = Transfer.objects.filter(
            is_basic_domestic_need=True,
            source_party=party,
            reporting_period__name=period_name,
            substance__group=group
        )
        transfer_odp = Decimal(0)
        for tx in transfers:
            transfer_odp += tx.transferred_amount * tx.substance.odp
        return transfer_odp

    def production(self, party, group, periods):
        if len(periods) != 1:
            raise CommandError(
                f"Production func should have only one period parameter,"
                "got {periods}"
            )
        prodcons = self._get_prodcons(party, group, periods[0])
        if not prodcons:
            return None
        return prodcons.calculated_production \
            if prodcons.calculated_production > 0 else Decimal('0.0')

    def average_production(self, party, group, periods):
        total_prod = Decimal('0.0')
        rounding_digits = 0
        for period in periods:
            prodcons = self._get_prodcons(party, group, period)
            if not prodcons:
                return None
            total_prod += prodcons.calculated_production
            rounding_digits = max(rounding_digits, prodcons.decimals)

        average_prod = round_decimal_half_up(
            total_prod / len(periods),
            rounding_digits
        )
        return average_prod if average_prod > 0 else Decimal('0')

    def average_production_bdn(self, party, group, periods):
        total_prod = Decimal('0.0')
        for period in periods:
            prodcons = self._get_prodcons(party, group, period)
            if not prodcons:
                return None
            total_prod += prodcons.production_article_5
            if total_prod > 0:
                # Special case, e.g. France/AI (no production, only transfers)
                total_prod += self._get_bdn_transfer(party, group, period)

        average_prod = round_decimal_half_up(total_prod / len(periods), 5)
        return average_prod if average_prod > 0 else Decimal('0')

    def consumption(self, party, group, periods):
        # EU member states don't have this baseline
        if len(periods) != 1:
            raise CommandError(
                f"Consumption func should have only one period parameter,"
                "got {periods}"
            )
        prodcons = self._get_prodcons(party, group, periods[0])
        if not prodcons or prodcons.is_eu_member:
            return None
        return prodcons.calculated_consumption \
            if prodcons.calculated_consumption > 0 else Decimal('0')

    def average_consumption(self, party, group, periods):
        total_cons = Decimal('0.0')
        rounding_digits = 0
        for period in periods:
            prodcons = self._get_prodcons(party, group, period)
            if not prodcons or prodcons.is_eu_member:
                return None
            total_cons += prodcons.calculated_consumption
            if group.group_id in ('AI', 'AII', 'BI', 'BII', 'BIII'):
                # Add ImpRecov and subtract ExpRecov
                total_cons += prodcons.import_recovered - prodcons.export_recovered
            rounding_digits = max(rounding_digits, prodcons.decimals)

        average_cons = round_decimal_half_up(
            total_cons / len(periods),
            rounding_digits
        )
        return average_cons if average_cons > 0 else Decimal('0')

    def production_ci_na5(self, party, _group, _periods):
        """ Average of
            1989 HCFC production + 2.8 per cent of 1989 CFC production
            and
            1989 HCFC consumption + 2.8 per cent of 1989 CFC consumption
        """

        hcfc_group = self.groups.get('CI')
        cfc_group = self.groups.get('AI')
        hcfc_1989 = self._get_prodcons(party, hcfc_group, '1989')
        cfc_1989 = self._get_prodcons(party, cfc_group, '1989')
        if hcfc_1989 and cfc_1989:
            # Note: For EU members, real consumption is included in the formula
            # even if they have NULL calculated_consumption
            average_prod = sum_decimals(
                    hcfc_1989.calculated_production,
                    cfc_1989.calculated_production * Decimal('0.028'),
                    hcfc_1989.get_calc_consumption(),
                    cfc_1989.get_calc_consumption() * Decimal('0.028')
            )
            average_prod = round_decimal_half_up(
                average_prod / 2,
                1  # always 1 decimal for 1989
            )
            return average_prod if average_prod > 0 else Decimal('0')
        return None

    def consumption_ci_na5(self, party, _group, _periods):
        """
            1989 HCFC consumption + 2.8 per cent of 1989 CFC consumption
        """
        hcfc_group = self.groups.get('CI')
        cfc_group = self.groups.get('AI')
        hcfc_1989 = self._get_prodcons(party, hcfc_group, '1989')
        cfc_1989 = self._get_prodcons(party, cfc_group, '1989')
        if hcfc_1989 and cfc_1989:
            if hcfc_1989.is_eu_member:
                return None
            average_cons = round_decimal_half_up(
                hcfc_1989.calculated_consumption +
                cfc_1989.calculated_consumption * Decimal('0.028'),
                hcfc_1989.decimals
            )
            return average_cons if average_cons > 0 else Decimal('0')
        return None

    def _get_hcfc_percentage(self, party):
        """
            Returns the percentage of the HCFC baseline included in
            the formula for the HFC baseline
            15% for NA5G1
            25% for NA5G2
            65% for A5 (G1 and G2)
        """
        party_type = PartyHistory.objects.get(
            party=party,
            reporting_period=ReportingPeriod.get_current_period(),
        ).party_type.abbr
        return {
            'NA5G1': Decimal('0.15'),
            'NA5G2': Decimal('0.25'),
            'A5G1': Decimal('0.65'),
            'A5G2': Decimal('0.65'),
        }.get(party_type)

    def production_f_na5(self, party, _group, _periods):
        return self._prod_cons_f(party, _group, _periods, 'PROD', 'NA5')

    def consumption_f_na5(self, party, _group, _periods):
        return self._prod_cons_f(party, _group, _periods, 'CONS', 'NA5')

    def production_f_a5(self, party, _group, _periods):
        return self._prod_cons_f(party, _group, _periods, 'PROD', 'A5')

    def consumption_f_a5(self, party, _group, _periods):
        return self._prod_cons_f(party, _group, _periods, 'CONS', 'A5')

    def _prod_cons_f(self, party, _group, _periods, prod_cons, base_party_type):
        """
            HFC baseline actually depends on the party group:

            NA5 Group 1: Average HFC for 2011-2013 + 15% of HCFC baseline
            NA5 Group 2: Average HFC for 2011-2013 + 25% of HCFC baseline
             A5 Group 1: Average HFC for 2020–2022 + 65% of HCFC baseline
             A5 Group 2: Average HFC for 2024–2026 + 65% of HCFC baseline
        """
        try:
            current_period = ReportingPeriod.get_current_period()
            party_type = PartyHistory.objects.get(
                party=party,
                reporting_period=current_period,
            ).party_type.abbr
            if not party_type.startswith(base_party_type):
                return None
        except PartyHistory.DoesNotExist:
            # can happen for Palestine or new states
            logger.warning(f"No party history for {party.abbr}/{current_period.name}")
            return None

        base_periods = {
            'NA5G1': ('2011', '2012', '2013'),
            'NA5G2': ('2011', '2012', '2013'),
            'A5G1': ('2020', '2021', '2022'),
            'A5G2': ('2024', '2025', '2026'),
        }.get(party_type)

        hfc_group = self.groups.get('F')
        total_amount = Decimal('0.0')
        for period in base_periods:
            prodcons = self._get_prodcons(party, hfc_group, period)
            if not prodcons:
                # If data not reported, no baseline is computed
                return None
            if prod_cons == 'PROD':
                total_amount += prodcons.calculated_production
            elif prod_cons == 'CONS':
                total_amount += prodcons.calculated_consumption
        if total_amount < 0:
            total_amount = Decimal('0')

        hcfc_group = self.groups.get('CI')
        hcfc_baseline_type = {
            ('PROD', 'NA5G1'): 'NA5ProdGWP',
            ('PROD', 'NA5G2'): 'NA5ProdGWP',
            ('PROD', 'A5G1'): 'A5ProdGWP',
            ('PROD', 'A5G2'): 'A5ProdGWP',
            ('CONS', 'NA5G1'): 'NA5ConsGWP',
            ('CONS', 'NA5G2'): 'NA5ConsGWP',
            ('CONS', 'A5G1'): 'A5ConsGWP',
            ('CONS', 'A5G2'): 'A5ConsGWP',
        }.get(
            (prod_cons, party_type)
        )
        hcfc_baseline = self.get_baseline(hcfc_baseline_type, hcfc_group, party)
        if hcfc_baseline is None:
            return None

        rounded_average = round_decimal_half_up(
            (
                total_amount / len(base_periods) +
                self._get_hcfc_percentage(party) * hcfc_baseline
            ),
            0
        )
        return rounded_average if rounded_average > 0 else Decimal('0')

    def baseline_NA5Prod(self, group, party):
        if party.abbr == 'EU':
            # EU doesn't have this baseline
            return None, None

        if group.group_id in ('AI', 'AII'):
            periods = ('1986',)
            func = self.production
        elif group.group_id in ('BI', 'BII', 'BIII'):
            periods = ('1989',)
            func = self.production
        elif group.group_id in ('CI'):
            periods = ('1989',)
            func = self.production_ci_na5
        elif group.group_id in ('CII', 'CIII'):
            periods = None
            func = None
        elif group.group_id in ('EI'):
            periods = ('1991',)
            func = self.production
        elif group.group_id in ('F'):
            periods = None
            func = self.production_f_na5

        return func, periods

    def baseline_NA5Cons(self, group, party):
        if party.abbr in self.eu_member_states:
            # EU member states don't have this baseline
            return None, None
        if group.group_id in ('AI', 'AII'):
            periods = ('1986',)
            func = self.consumption
        elif group.group_id in ('BI', 'BII', 'BIII'):
            periods = ('1989',)
            func = self.consumption
        elif group.group_id in ('CI'):
            periods = ('1989',)
            func = self.consumption_ci_na5
        elif group.group_id in ('CII', 'CIII'):
            periods = None
            func = None
        elif group.group_id in ('EI'):
            periods = ('1991',)
            func = self.consumption
        elif group.group_id in ('F'):
            periods = None
            func = self.consumption_f_na5

        return func, periods

    def baseline_A5Prod(self, group, party):
        if party.abbr == 'EU':
            # EU doesn't have this baseline
            return None, None

        if group.group_id in ('AI', 'AII'):
            periods = ('1995', '1996', '1997')
            func = self.average_production
        elif group.group_id in ('BI', 'BII', 'BIII'):
            periods = ('1998', '1999', '2000')
            func = self.average_production
        elif group.group_id in ('CI'):
            periods = ('2009', '2010')
            func = self.average_production
        elif group.group_id in ('CII', 'CIII'):
            periods = None
            func = None
        elif group.group_id in ('EI'):
            periods = ('1995', '1996', '1997', '1998')
            func = self.average_production
        elif group.group_id in ('F'):
            periods = None
            func = self.production_f_a5

        return func, periods

    def baseline_A5Cons(self, group, party):
        if party.abbr in self.eu_member_states:
            # EU member states don't have this baseline
            return None, None
        if group.group_id in ('AI', 'AII'):
            periods = ('1995', '1996', '1997')
            func = self.average_consumption
        elif group.group_id in ('BI', 'BII', 'BIII'):
            periods = ('1998', '1999', '2000')
            func = self.average_consumption
        elif group.group_id in ('CI'):
            periods = ('2009', '2010')
            func = self.average_consumption
        elif group.group_id in ('CII', 'CIII'):
            periods = None
            func = None
        elif group.group_id in ('EI'):
            periods = ('1995', '1996', '1997', '1998')
            func = self.average_consumption
        elif group.group_id in ('F'):
            periods = None
            func = self.consumption_f_a5

        return func, periods

    def baseline_BDN_NA5(self, group, party):
        if party.abbr == 'EU':
            # EU doesn't have this baseline
            return None, None
        if group.group_id in ('AI', 'AII'):
            periods = ('1995', '1996', '1997')
            func = self.average_production_bdn
        elif group.group_id in ('BI'):
            periods = ('1998', '1999', '2000')
            func = self.average_production_bdn
        elif group.group_id in ('BII', 'BIII', 'CI', 'CII', 'CIII', 'F'):
            periods = None
            func = None
        elif group.group_id in ('EI'):
            periods = ('1995', '1996', '1997', '1998')
            func = self.average_production_bdn
        return func, periods

    def _prod_cons_gwp(self, party, group, period_name, prod_or_cons):
        """
        Normally should be invoked only for groups A/I (CFC) and C/I (HCFC).
        prod_or_cons should be 'PROD' or 'CONS'.
        """
        prodcons = self._get_prodcons(party, group, period_name)
        if not prodcons:
            return None

        submission_id = prodcons.submissions.get('art7')[0]
        submission = Submission.objects.get(pk=submission_id)
        agg = submission.get_aggregated_data(baseline=True).get(group)
        if prod_or_cons == 'PROD':
            return agg.calculated_production
        else:
            return agg.calculated_consumption

    def consumption_ci_na5_gwp(self, party, _group, _periods):
        """
            The HFC baseline includes a % of the HCFC baseline
            computed in CO2-equivalent tonnes
            The HCFC baseline formula contains in its turn a percentage of
            the CFC production/consumption
        """
        cfc_group = self.groups.get('AI')
        hcfc_group = self.groups.get('CI')
        hcfc_cons = self._prod_cons_gwp(party, hcfc_group, '1989', 'CONS')
        cfc_cons = self._prod_cons_gwp(party, cfc_group, '1989', 'CONS')
        if hcfc_cons is None or cfc_cons is None:
            return None

        if party.abbr == 'EU':
            # Must add consumption of EU member states
            # which were not member states in 1989
            for _ms in self.new_eu_member_states_since['1989']:
                hcfc_cons_ms = self._prod_cons_gwp(_ms, hcfc_group, '1989', 'CONS')
                if hcfc_cons_ms is not None and hcfc_cons_ms > 0:
                    hcfc_cons += hcfc_cons_ms
                cfc_cons_ms = self._prod_cons_gwp(_ms, cfc_group, '1989', 'CONS')
                if cfc_cons_ms is not None and cfc_cons_ms > 0:
                    cfc_cons += cfc_cons_ms
                logger.debug(f"{_ms.abbr} cfc={cfc_cons_ms} hcfc={hcfc_cons_ms}")

        rounded_average = round_decimal_half_up(
            round_decimal_half_up(hcfc_cons, 0) +
            round_decimal_half_up(cfc_cons, 0) * Decimal('0.028'),
            0
        )
        return rounded_average if rounded_average > 0 else Decimal('0')

    def production_ci_na5_gwp(self, party, _group, _periods):
        """
            The HFC baseline includes a % of the HCFC baseline
            computed in CO2-equivalent tonnes
            The HCFC baseline formula contains in its turn a percentage of
            the CFC production/consumption
        """
        cfc_group = self.groups.get('AI')
        hcfc_group = self.groups.get('CI')

        # Note that the consumption of EU member states SHOULD BE included!
        # Also, these should be unrounded values!
        hcfc_prod = self._prod_cons_gwp(party, hcfc_group, '1989', 'PROD')
        cfc_prod = self._prod_cons_gwp(party, cfc_group, '1989', 'PROD')
        hcfc_cons = self._prod_cons_gwp(party, hcfc_group, '1989', 'CONS')
        cfc_cons = self._prod_cons_gwp(party, cfc_group, '1989', 'CONS')

        if any(x is None for x in (hcfc_prod, cfc_prod, hcfc_cons, cfc_cons)):
            return None

        rounded_average = round_decimal_half_up((
            round_decimal_half_up(hcfc_prod, 0) +
            round_decimal_half_up(cfc_prod, 0) * Decimal('0.028') +
            round_decimal_half_up(hcfc_cons, 0) +
            round_decimal_half_up(cfc_cons, 0) * Decimal('0.028')
        ) / 2, 0)
        return rounded_average if rounded_average > 0 else Decimal('0')

    def average_production_gwp(self, party, group, periods):
        total_prod = Decimal('0.0')
        for period in periods:
            prod = self._prod_cons_gwp(party, group, period, 'PROD')
            if prod is None:
                # Don't compute if party has not reported for a baseline period
                return None
            total_prod += round_decimal_half_up(prod, 0)

        rounded_average = round_decimal_half_up(
            total_prod / len(periods), 0
        )
        return rounded_average if rounded_average > 0 else Decimal('0')

    def average_consumption_gwp(self, party, group, periods):
        total_cons = Decimal('0.0')
        for period in periods:
            cons = self._prod_cons_gwp(party, group, period, 'CONS')
            if cons is None:
                # Don't compute if party has not reported for a baseline period
                return None
            total_cons += round_decimal_half_up(cons, 0)

            if party.abbr == 'EU':
                # Must add consumption of EU member states
                # which were not member states in 1989
                for _ms in self.new_eu_member_states_since[period]:
                    cons_ms = self._prod_cons_gwp(_ms, group, period, 'CONS')
                    if cons_ms is not None:
                        total_cons += round_decimal_half_up(cons_ms, 0)

        rounded_average = round_decimal_half_up(
            total_cons / len(periods), 0
        )
        return rounded_average if rounded_average > 0 else Decimal('0')

    def baseline_NA5ProdGWP(self, group, party):
        # only for group C/I, which is part of the HFC baseline formula
        if party.abbr == 'EU':
            # EU doesn't have this baseline
            return None, None

        if group.group_id in ('CI'):
            periods = ('1989',)
            func = self.production_ci_na5_gwp
        elif group.group_id in ('F'):
            periods = None
            func = self.production_f_na5
        else:
            periods = None
            func = None
        return func, periods

    def baseline_NA5ConsGWP(self, group, party):
        # only for group C/I, which is part of the HFC baseline formula
        if party.abbr in self.eu_member_states:
            # EU member states don't have this baseline
            return None, None
        if group.group_id in ('CI',):
            periods = ('1989',)
            func = self.consumption_ci_na5_gwp
        elif group.group_id in ('F'):
            periods = None
            func = self.consumption_f_na5
        else:
            periods = None
            func = None

        return func, periods

    def baseline_A5ProdGWP(self, group, party):
        # only for group C/I, which is part of the HFC baseline formula
        if party.abbr == 'EU':
            # EU doesn't have this baseline
            return None, None

        if group.group_id in ('CI'):
            periods = ('2009', '2010')
            func = self.average_production_gwp
        elif group.group_id in ('F'):
            periods = None
            func = self.production_f_a5
        else:
            periods = None
            func = None
        return func, periods

    def baseline_A5ConsGWP(self, group, party):
        # only for group C/I, which is part of the HFC baseline formula
        if party.abbr in self.eu_member_states:
            # EU member states don't have this baseline
            return None, None
        if group.group_id in ('CI',):
            periods = ('2009', '2010')
            func = self.average_consumption_gwp
        elif group.group_id in ('F'):
            periods = None
            func = self.consumption_f_a5
        else:
            periods = None
            func = None

        return func, periods
