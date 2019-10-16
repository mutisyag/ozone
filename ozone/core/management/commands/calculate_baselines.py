import logging

from django.core.management.base import BaseCommand
from openpyxl import load_workbook
import collections

from ozone.core.models import (
    Party,
    ProdCons,
    BaselineType,
    Baseline,
)
from ozone.core.models.utils import (
    float_to_decimal,
    float_to_decimal_zero_if_none,
)
from ozone.core.calculated import baselines

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = __doc__

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super().__init__(stdout=None, stderr=None, no_color=False)
        self.calculator = baselines.BaselineCalculator()

    def add_arguments(self, parser):
        parser.add_argument(
            '--party',
            help="Party code, for limiting the calculation to a single party"
        )
        parser.add_argument(
            '--baseline_types',
            nargs='*',
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
        baselines.logger.addHandler(stream)
        baselines.logger.setLevel(logging.INFO)

        if int(options['verbosity']) > 1:
            logger.setLevel(logging.DEBUG)
            baselines.logger.setLevel(logging.DEBUG)

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
            party = self.calculator.parties[pk[0]]
            suffix = ''
            if not pk[3]:
                # this is GWP baseline for A/I, C/I or F
                group_name = (pk[2] + 'I') if pk[2] in ['A', 'C'] else pk[2]
                suffix = 'GWP'
            else:
                group_name = pk[2] + pk[3]
            group = self.calculator.groups[group_name]
            for kind in ('Prod', 'Cons'):
                baseline_type = pk[1] + kind + suffix
                computed = self.calculator.get_baseline(baseline_type, group, party)
                legacy = float_to_decimal(row["Calc" + kind])
                log_line = f"{pk} Calc{kind} computed={computed} legacy={legacy}"
                logger.debug(f"Checking {log_line}")
                if computed != legacy and not (
                    # Skip some known issues when computed is None for EU members
                    legacy is None and party.abbr in self.calculator.eu_member_states and (
                        baseline_type in ('A5Cons', 'NA5Cons') or
                        baseline_type == 'NA5ConsGWP' and group_name == 'CI'
                    ) or
                    legacy is None and party.abbr == 'EU' and (
                        baseline_type in ('A5Prod', 'NA5Prod')
                    ) or
                    computed is None and party.abbr == 'EU' and (
                        baseline_type in ('A5ProdGWP', 'NA5ProdGWP')
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
                computed = self.calculator.get_baseline('BDN_NA5', group, party)
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
        baseline_types = options.get('baseline_types')

        for group in self.calculator.groups.values():
            must_update_prodcons = False
            for baseline_type in BaselineType.objects.all():
                if baseline_types and baseline_type.name not in baseline_types:
                    continue
                baseline = self.calculator.get_baseline(baseline_type.name, group, party)
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
