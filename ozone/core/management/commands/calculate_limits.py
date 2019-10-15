import logging

from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db.models import Q

from openpyxl import load_workbook
import collections

from ozone.core.models import (
    Party,
    PartyHistory,
    ReportingPeriod,
    Group,
    ProdCons,
    Limit,
    Baseline,
    ControlMeasure,
    LimitTypes,
)

from ozone.core.models.utils import (
    round_decimal_half_up,
    float_to_decimal,
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
            '--period',
            help="Period name, for limiting the calculation to a single period"
        )
        parser.add_argument(
            '--simulate',
            action='store_true',
            help="Don't store any change, only simulate"
        )
        parser.add_argument(
            '--test_file',
            help="Location of the legacy_bdn_limits.xlsx file "
            "for checking computed values (BDN_NA5 limits only) with legacy data"
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

        if not ControlMeasure.objects.exists():
            logger.error("Control measures not found, aborting.")
            return

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
        sheet = wb['BDNProdLimitsNew']
        values = list(sheet.values)
        results = collections.defaultdict(list)
        headers = values[0]
        for row in values[1:]:
            row = dict(zip(headers, row))
            pk = row["CntryID"], row["PeriodID"], row["Anx"], row["Grp"]
            results[pk] = row
        return results

    def test_legacy_data(self, results):
        errors = list()
        for pk, row in results.items():
            # key = (CntryId, Period, Anx, Grp)
            party = self.parties[pk[0]]
            period = self.reporting_periods[pk[1]]
            group = self.groups[pk[2]+pk[3]]
            party_type = PartyHistory.objects.get(
                party=party,
                reporting_period=period,
            ).party_type

            computed = self.get_limit(
                'BDN', group, party, party_type, period
            )
            legacy = float_to_decimal(row['BDNProdLimit'])
            log_line = f"{pk} Computed={computed} legacy={legacy}"
            if computed != legacy:
                logger.error(f"Failed for {log_line}")
                errors.append(f"{log_line}")

        if errors:
            logger.error(f"Total errors: {len(errors)}")
            logger.error("\n".join(errors))
        else:
            logger.info("All checks passed. Good job!")

    def process_party(self, party, options):
        logger.info(f"Processing party {party.abbr} {party.name}")
        qs = PartyHistory.objects.filter(
            party=party
        ).order_by('reporting_period__start_date')

        if options['period']:
            qs = qs.filter(
                reporting_period__name=options['period']
            )

        for party_history in qs:
            party = party_history.party
            party_type = party_history.party_type
            period = party_history.reporting_period

            if period.is_control_period:
                # No limits for control periods
                continue
            logger.debug('Processing party {}({}) and period {}'.format(
                party.abbr, party.name, period.name
            ))
            for group in self.groups.values():
                has_changed = False
                for limit_type in LimitTypes:
                    limit = self.get_limit(
                        limit_type.value, group, party, party_type, period
                    )
                    if limit is not None:
                        logger.debug("Got {:10f} for {}/{}/{}/{}".format(
                            limit,
                            party.abbr,
                            limit_type.name,
                            group.group_id,
                            period.name,
                        ))
                    if options['simulate']:
                        continue

                    has_changed |= self._persist_limit(
                        limit_type.value, group, party, period, limit
                    )
                if has_changed:
                    # invoke after all limit types for this group are computed
                    self._update_prodcons(group, party, period)

    def _persist_limit(self, limit_type, group, party, period, new_value):
        has_changed = False
        if new_value is None:
            count, _ = Limit.objects.filter(
                party=party,
                group=group,
                reporting_period=period,
                limit_type=limit_type,
            ).delete()
            if count > 0:
                logger.info("Deleted previous limit for {}/{}/{}/{}".format(
                    party.abbr,
                    limit_type,
                    group.group_id,
                    period.name,
                ))
                has_changed = True
        else:
            # get_or_create insteadof update_or_create to log only real changes
            obj, _created = Limit.objects.get_or_create(
                party=party,
                group=group,
                reporting_period=period,
                limit_type=limit_type,
            )
            if _created:
                logger.info("Creating new limit for {}/{}/{}/{} = {}".format(
                    party.abbr,
                    limit_type,
                    group.group_id,
                    period.name,
                    new_value,
                ))
                has_changed = True
            elif obj.limit != new_value:
                has_changed = True
                logger.info("Updating limit for {}/{}/{}/{} from {} to {}".format(
                    party.abbr,
                    limit_type,
                    group.group_id,
                    period.name,
                    obj.limit,
                    new_value,
                ))
            obj.limit = new_value
            obj.save()
        return has_changed

    def _update_prodcons(self, group, party, period):
        qs = ProdCons.objects.filter(
            party=party,
            group=group,
            reporting_period=period,
        )
        for prodcons in qs.all():
            prodcons.populate_limits_and_baselines()
            logger.debug("Updating ProdCons for {}/{}/{}".format(
                party.abbr, group.group_id, period.name
            ))
            prodcons.save()

    def _get_baseline(self, party, group, baseline_type):
        if group.group_id in ('CII', 'CIII'):
            # Fake baseline, because control measures start with phase-out
            return Decimal(0)
        else:
            baseline = Baseline.objects.filter(
                party=party,
                group=group,
                baseline_type=baseline_type
            ).first()
            if baseline is None:
                return None
            else:
                return baseline.baseline

    def _get_decimals_for_limits(self, group, party):
        """
            Limits must use the same number of decimals as baselines.
            Meaning that for C/I we only use one decimal, unless party is
              in that special list, because C/I baseline for A5
              is the everage of 2009 and 2010
        """
        if group.group_id == 'F':
            return 0
        elif group.group_id == 'CI' and (
            party.abbr in ProdCons.special_cases_2009 or
            party.abbr in ProdCons.special_cases_2010
        ):
            return 2
        return 1

    def get_limit(self, limit_type, group, party, party_type, period):

        if party.abbr == 'EU' and limit_type in (
            LimitTypes.BDN.value,
            LimitTypes.PRODUCTION.value
        ):
            # No BDN or Prod limits for EU/ECE(European Union)
            return None

        if (
            party in Party.get_eu_members_at(period) and
            limit_type == LimitTypes.CONSUMPTION.value
        ):
            # No consumption baseline for EU member states
            return None

        cm_queryset = ControlMeasure.objects.filter(
            group=group,
            party_type=party_type,
            start_date__lte=period.end_date,
            limit_type=limit_type,
        ).filter(
            Q(end_date__gte=period.start_date) | Q(end_date__isnull=True)
        ).order_by('start_date')
        cm_count = cm_queryset.count()
        if cm_count == 0:
            # No control measures here
            return None
        elif cm_count == 1:
            cm = cm_queryset.first()
            baseline = self._get_baseline(party, group, cm.baseline_type)
            if baseline is None:
                return Decimal('0')
            else:
                return round_decimal_half_up(
                    baseline * cm.allowed,
                    self._get_decimals_for_limits(group, party)
                )
        elif cm_count == 2:
            # This happens for NA5 BDN limits, AI/BI/EI
            # because control measure becomes applicable in July 28, 2000
            cm1 = cm_queryset[0]
            cm2 = cm_queryset[1]
            baseline1 = self._get_baseline(party, group, cm1.baseline_type)
            baseline2 = self._get_baseline(party, group, cm2.baseline_type)
            if baseline1 is None or baseline2 is None:
                return Decimal('0')
            days1 = (cm1.end_date - period.start_date).days + 1
            days2 = (period.end_date - cm2.start_date).days + 1
            limit = (
                cm1.allowed * days1 * baseline1 +
                cm2.allowed * days2 * baseline2
            ) / ((period.end_date - period.start_date).days + 1)
            return round_decimal_half_up(
                limit,
                self._get_decimals_for_limits(group, party)
            )
