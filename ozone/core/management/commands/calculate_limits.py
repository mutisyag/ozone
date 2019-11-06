import logging

from django.core.management.base import BaseCommand

from openpyxl import load_workbook
import collections

from ozone.core.models import (
    Party,
    PartyHistory,
    ProdCons,
    Limit,
    ControlMeasure,
    LimitTypes,
)

from ozone.core.models.utils import float_to_decimal

from ozone.core.calculated import limits

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = __doc__

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super().__init__(stdout=None, stderr=None, no_color=False)
        self.calculator = limits.LimitCalculator()

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
        limits.logger.addHandler(stream)
        limits.logger.setLevel(logging.INFO)

        if int(options['verbosity']) > 1:
            logger.setLevel(logging.DEBUG)
            limits.logger.setLevel(logging.DEBUG)

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
            party = self.calculator.parties[pk[0]]
            period = self.calculator.reporting_periods[pk[1]]
            group = self.calculator.groups[pk[2] + pk[3]]
            ph = PartyHistory.objects.get(
                party=party,
                reporting_period=period,
            )
            party_type = ph.party_type
            is_eu_member = ph.is_eu_member

            computed = self.calculator.get_limit(
                'BDN', group, party, party_type, is_eu_member, period
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
            is_eu_member = party_history.is_eu_member
            period = party_history.reporting_period

            if period.is_control_period:
                # No limits for control periods
                continue
            logger.debug('Processing party {}({}) and period {}'.format(
                party.abbr, party.name, period.name
            ))
            for group in self.calculator.groups.values():
                has_changed = False
                for limit_type in LimitTypes:
                    limit = self.calculator.get_limit(
                        limit_type.value,
                        group, party,
                        party_type,
                        is_eu_member,
                        period
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
