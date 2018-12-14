"""Import Submission from Excel file.
"""
import pickle
import decimal
import logging
import collections

from django.core.management.base import BaseCommand
from django.db import transaction
from openpyxl import load_workbook

from ozone.core.models import User
from ozone.core.models import Party
from ozone.core.models import Substance
from ozone.core.models import Submission
from ozone.core.models import Article7Import
from ozone.core.models import Article7Export
from ozone.core.models import SubmissionInfo
from ozone.core.models import ReportingPeriod
from ozone.core.models import Article7Production
from ozone.core.models import Article7Destruction
from ozone.core.models import Article7NonPartyTrade
from ozone.core.models import Article7Questionnaire

logger = logging.getLogger(__name__)
CACHE_LOC = "/var/tmp/legacy_submission.cache"


class Command(BaseCommand):
    help = "Import Submission from Excel file"
    # Used for double checks.
    import_types = (
        "ImpNew",
        "ImpRecov",
        "ImpFeedstock",
        "ImpEssenUse",
        "ImpProcAgent",
        "ImpQuarAppl",
        # "ImpLabUse",
        "ImpPolyol",
    )

    data_to_check = (
        "imports",
        "exports",
        "produced",
        "destroyed",
        # "nonparty",
    )

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super().__init__(stdout=None, stderr=None, no_color=False)

        # Load all values in memory for faster lookups.
        self.current_submission = set(Submission.objects.filter(obligation_id=1).values_list(
            "party__abbr", "reporting_period__name"
        ))
        self.periods = {_period.name: _period
                        for _period in ReportingPeriod.objects.all()}
        self.parties = {_party.abbr: _party
                        for _party in Party.objects.all()}
        self.substances = {_substance.substance_id: _substance
                           for _substance in Substance.objects.all()}

        self.method = Submission.SubmissionMethods.LEGACY
        self.precision = 10

    def add_arguments(self, parser):
        parser.add_argument('file',
                            help="the xlsx input file")
        parser.add_argument('--recreate', action="store_true", default=False,
                            help="Re-create if submission already exists.")
        parser.add_argument('--purge', action="store_true", default=False,
                            help="Purge all entries that were imported")
        parser.add_argument('-l', '--limit', type=int, default=None,
                            help="Limit the number of row to import.")
        parser.add_argument('-p', '--precision', type=int, default=10,
                            help="Number of digits after after the period to "
                                 "check for consistency.")
        parser.add_argument('-C', '--use-cache', action="store_true", default=False,
                            help="Load the data from the cache (if available) instead "
                                 "of the xls")
        parser.add_argument("--dry-run", action="store_true", default=False,
                            help="Only parse the data, but do not insert it.")

    def process_entry(self, *args, **kwargs):
        """Process the parsed data and insert it into the DB.

        Only a wrapper, see _process_entry.
        """
        try:
            return self._process_entry(*args, **kwargs)
        except Exception as e:
            logger.error("Error %s while saving: %s", e, args[:2],
                         exc_info=True)
            return False

    def get_imports(self, row, party, period):
        """Parses the import data for the submission identified by
        the party/period combination.

        The same data data is duplicated in legacy Excel file. One
        version has the source_party information, and the other one
        only has the total for each submission. Because the source
        party information was introduced at a later time, and made
        optional.

        Double check that the data matches in both sheets and log
        warning if not.

        Return a list of imports.
        """
        imports = []

        # Double check the data from old import sheet with the
        # data from the new import sheet.
        double_check_new = collections.defaultdict(decimal.Decimal)
        double_check_old = collections.defaultdict(decimal.Decimal)

        for import_row in row["ImportNew"]:

            for imp_type in self.import_types:
                pk = party.abbr, period.name, import_row["SubstID"], imp_type
                double_check_new[pk] += decimal.Decimal(import_row[imp_type] or 0)

            # Get the source party, if not present then add it as NULL
            # the data on the source party will be in the remarks.
            source_party = import_row["OrgCntryID"].upper()
            if source_party in ("ZZB", "UNK"):
                source_party_id = None
            else:
                try:
                    source_party_id = self.parties[source_party].id
                except KeyError as e:
                    logger.error("Import new unknown source party %s: %s/%s", e, party.abbr,
                                 period.name)
                    source_party_id = None

            try:
                substance_id = self.substances[import_row["SubstID"]].id
            except KeyError as e:
                logger.error("Import new unknown substance %s: %s/%s", e, party.abbr, period.name)
                continue

            imports.append({
                "remarks_party": import_row["Remark"] or "",
                # "remarks_os": "",
                "source_party_id": source_party_id,
                "quantity_total_new": import_row["ImpNew"],
                "quantity_total_recovered": import_row["ImpRecov"],
                "quantity_feedstock": import_row["ImpFeedstock"],
                "quantity_critical_uses": None,
                "quantity_essential_uses": import_row["ImpEssenUse"],
                "quantity_high_ambient_temperature": None,
                "quantity_laboratory_analytical_uses": None,
                "quantity_process_agent_uses": import_row["ImpProcAgent"],
                "quantity_quarantine_pre_shipment": import_row["ImpQuarAppl"],
                "quantity_polyols": import_row["ImpPolyol"],
                "quantity_other_uses": None,
                "decision_critical_uses": "",
                "decision_essential_uses": "",
                "decision_high_ambient_temperature": "",
                "decision_laboratory_analytical_uses": "",
                "decision_process_agent_uses": "",
                "decision_quarantine_pre_shipment": "",
                "decision_other_uses": "",
                # "blend_id": "",
                # "blend_item_id": "", #???
                "substance_id": substance_id,
                # "ordering_id": "",
                # "submission_id": "", # Automatically filled.
            })

        # Cross-Reference with the other sheet, for a double check of data
        # consistency. Only use the ImportNew sheet for now.
        for import_row in row["Import"]:
            for imp_type in self.import_types:
                pk = party.abbr, period.name, import_row["SubstID"], imp_type
                double_check_old[pk] += decimal.Decimal(import_row[imp_type] or 0)

        self.double_check(double_check_old, double_check_new)

        return imports

    def double_check(self, old, new):
        """Compare the data from the 'Import' sheet with the data from
        the 'ImportNew' sheet. Log any inconsistencies.
        """
        # Iterate here instead of doing a simple check, so we print out
        # the errors with more details AND to the equals check up to a
        # certain precision because of the floating point operations.
        old = dict(old)
        new = dict(new)
        all_keys = set(list(old.keys()) + list(new.keys()))
        for key in all_keys:
            try:
                old_value = old[key]
            except KeyError:
                logger.warning("Import inconsistency found for %s, present in old but not in new.",
                               key)
                continue

            try:
                new_value = new[key]
            except KeyError:
                logger.warning("Import inconsistency found for %s, present in new but not in old.",
                               key)
                continue

            if abs(new_value - old_value) >= (0.1 ** self.precision):
                logger.warning("Import inconsistency found for %s, values differ old=%s new=%s",
                               key, old_value, new_value)
                continue

    def get_exports(self, row, party, period):
        """Parses the export data for the submission identified by
        the party/period combination.

        Returns a list of exports.
        """
        exports = []

        for exports_row in row["Export"]:
            # Get the source party, if not present then add it as NULL
            # the data on the source party will be in the remarks.
            destination_party = exports_row["DestCntryID"].upper()
            if destination_party in ("ZZB", "UNK"):
                destination_party_id = None
            else:
                try:
                    destination_party_id = self.parties[destination_party].id
                except KeyError as e:
                    logger.error("Export unknown source party %s: %s/%s", e, party.abbr,
                                 period.name)
                    destination_party_id = None

            try:
                substance_id = self.substances[exports_row["SubstID"]].id
            except KeyError as e:
                logger.error("Export unknown substance %s: %s/%s", e, party.abbr, period.name)
                continue

            exports.append({
                "remarks_party": exports_row["Remark"] or "",
                # "remarks_os": "",
                "destination_party_id": destination_party_id,
                "quantity_total_new": exports_row["ExpNew"],
                "quantity_total_recovered": exports_row["ExpRecov"],
                "quantity_feedstock": exports_row["ExpFeedstock"],
                "quantity_critical_uses": None,
                "quantity_essential_uses": exports_row["ExpEssenUse"],
                "quantity_high_ambient_temperature": None,
                "quantity_laboratory_analytical_uses": None,
                "quantity_process_agent_uses": exports_row["ExpProcAgent"],
                "quantity_quarantine_pre_shipment": exports_row["ExpQuarAppl"],
                "quantity_polyols": exports_row["ExpPolyol"],
                "quantity_other_uses": None,
                "decision_critical_uses": "",
                "decision_essential_uses": "",
                "decision_high_ambient_temperature": "",
                "decision_laboratory_analytical_uses": "",
                "decision_process_agent_uses": "",
                "decision_quarantine_pre_shipment": "",
                "decision_other_uses": "",
                # "blend_id": "",
                # "blend_item_id": "",
                "substance_id": substance_id,
                # "ordering_id": "",
                # "submission_id": "", # Automatically filled.
            })

        return exports

    def get_destroyed(self, row, party, period):
        """Parses the "destroyed" data for the submission identified by
        the party/period combination.

        Returns a list of destroyed substances.
        """
        destroyed = []

        for destroyed_row in row["Destroyed"]:
            try:
                substance_id = self.substances[destroyed_row["SubstID"]].id
            except KeyError as e:
                logger.error("Export unknown substance %s: %s/%s", e, party.abbr, period.name)
                continue

            destroyed.append({
                "remarks_party": destroyed_row["Remark"] or "",
                "substance_id": substance_id,
                # "remarks_os": "",
                "quantity_destroyed": destroyed_row["Destroyed"],
                # "blend_id": "",
                # "blend_item_id": "",
                # "submission_id": "", # Auto filled
                # "ordering_id": "",
            })

        return destroyed

    def get_produced(self, row, party, period):
        """Parses the "produced" data for the submission identified by
        the party/period combination.

        Returns a list of produced substances.
        """
        produce = []

        for produce_row in row["Produce"]:
            try:
                substance_id = self.substances[produce_row["SubstID"]].id
            except KeyError as e:
                logger.error("Export unknown substance %s: %s/%s", e, party.abbr, period.name)
                continue

            produce.append({
                "remarks_party": produce_row["Remark"] or "",
                "substance_id": substance_id,
                # "remarks_os": "",
                "quantity_critical_uses": None,
                "quantity_essential_uses": None,
                "quantity_high_ambient_temperature": None,
                "quantity_laboratory_analytical_uses": None,
                "quantity_process_agent_uses": produce_row["ProdProcAgent"],
                "quantity_quarantine_pre_shipment": produce_row["ProdQuarAppl"],
                "quantity_total_produced": produce_row["ProdAllNew"],
                "quantity_other_uses": None,
                "quantity_feedstock": produce_row["ProdFeedstock"],
                "quantity_article_5": produce_row["ProdArt5"],
                "quantity_for_destruction": None,
                "decision_critical_uses": "",
                "decision_essential_uses": "",
                "decision_high_ambient_temperature": "",
                "decision_laboratory_analytical_uses": "",
                "decision_process_agent_uses": "",
                "decision_quarantine_pre_shipment": "",
                "decision_other_uses": "",
                # "submission_id": "", # Auto filled
                # "ordering_id": "",
            })

        return produce

    def get_data(self, row, party, period):
        """Structure and parse the raw data from the Excel file
        so it matches our models.
        """
        # There should only be one entry in the overall sheet.
        try:
            overall = row["Overall"][0]
        except IndexError as e:
            logger.warning("Overall sheet missing for: %s", row)
            return

        return {
            "submission": {
                "schema_version": "legacy",
                "filled_by_secretariat": False,
                "created_at": overall["DateCreate"],
                "updated_at": overall["DateUpdate"],
                "version": 1,
                "_workflow_class": "default",
                "_current_state": "finalized",
                "_previous_state": None,
                "flag_provisional": False,
                "flag_valid": True,
                "flag_superseded": False,
                "submitted_via": self.method,
                "remarks_party": overall["Remark"] or "",
                "remarks_secretariat": overall["SubmissionType"] or "",
                "created_by_id": self.admin.id,
                "last_edited_by_id": self.admin.id,
                "obligation_id": 1,
                "party_id": party.id,
                "reporting_period_id": period.id,
                "cloned_from_id": None,
                # "info_id": "",
            },
            "submission_info": {
                "reporting_officer": "",
                "designation": "",
                "organization": "",
                "postal_code": "",
                "country": party.name,
                "phone": "",
                "fax": "",
                "email": "",
                "date": overall["DateReported"],
            },
            "art7": {
                "remarks_party": "",
                "remarks_os": "",
                "has_imports": overall["Imported"],
                "has_exports": overall["Exported"],
                "has_produced": overall["Produced"],
                "has_destroyed": overall["Destroyed"],
                "has_nonparty": overall["NonPartyTrade"],
                "has_emissions": False,
                # "submission_id": "",
            },
            "art7_flags": {
                # TODO
            },
            "imports": self.get_imports(row, party, period),
            "exports": self.get_exports(row, party, period),
            "produced": self.get_produced(row, party, period),
            "destroyed": self.get_destroyed(row, party, period),
        }

    def check_consistency(self, data, party, period):
        """Check consistency of the data returned by get_data.

        Checks if the data is present the corresponding `has_*` flag
        is correctly set and the other way around.

        Log any inconsistencies, and returns True if the data looks
        to be valid, and False otherwise.
        """
        is_ok = True
        for data_type in self.data_to_check:
            # Check can be done in a single operation, but we want
            # to be verbose to log the inconsistency.
            if data[data_type] and not data["art7"]["has_" + data_type]:
                logger.warning("Inconsistency for %s/%s/%s: has data, but flag is not set",
                               party.abbr, period.name, data_type)
                is_ok = False
            elif not data[data_type] and data["art7"]["has_" + data_type]:
                logger.warning("Inconsistency for %s/%s/%s: does not have data, but flag set",
                               party.abbr, period.name, data_type)
                is_ok = False
        return is_ok

    @transaction.atomic
    def _process_entry(self, party, period, values, recreate=False, purge=False):
        """Inserts the processed data into the DB."""
        is_processed = (party.abbr, period.name) in self.current_submission
        if purge:
            self.delete_instance(party, period)
            return True

        if is_processed:
            if recreate:
                self.delete_instance(party, period)
            else:
                logger.info("Submission %s/%s already imported, skipping.",
                            party.abbr, period.name)
                return False

        submission = Submission.objects.create(**values["submission"])
        submission_info = SubmissionInfo.objects.create(
            submission=submission,
            **values["submission_info"],
        )
        art7 = Article7Questionnaire.objects.create(
            submission=submission,
            **values["art7"],
        )

        for import_values in values["imports"]:
            Article7Import.objects.create(submission=submission, **import_values)

        for export_values in values["exports"]:
            Article7Export.objects.create(submission=submission, **export_values)

        for produce_values in values["produce"]:
            Article7Production.objects.create(submission=submission, **produce_values)

        for destroyed_values in values["destroyed"]:
            Article7Destruction.objects.create(submission=submission, **destroyed_values)

        # Extra tidy
        submission._current_state = "finalized"
        submission.save()
        for obj in submission.history.all():
            obj.history_user = self.admin
            obj.save()

        log_data = ", ".join("%s=%s" % (_data_type, len(values[_data_type]))
                             for _data_type in self.data_to_check)
        logger.info("Submission %s/%s imported with %s",
                    party.abbr, period.name, log_data)
        return True

    def delete_instance(self, party, period):
        """Removes the submission identified by the party and period
        and any related data.
        """
        s = Submission.objects.filter(
            party=party,
            reporting_period=period,
        ).get()
        logger.info("Deleting submission %s", s.id)
        for related_data in s.RELATED_DATA:
            for instance in getattr(s, related_data).all():
                logger.debug("Deleting related data: %s", instance)
                instance.delete()
        s.__class__.data_changes_allowed = True
        s.delete()

    def load_workbook(self, filename, use_cache=False):
        """Loads the Excel file, collating the data based on the
        CntryID and PeriodID.

        If cache is set to True, then the data is loaded from a previously
        loaded version of the file. Reduces time required while doing a lot
        of tests.

        Returns a list in the following format:
        {
            ("RO", 2019): {
                "Overall": [{<overall-data>}],
                "Import": [{<import1>}, {<import2?}, ...]
                ...
            }
            ...
        }
        """
        if use_cache:
            try:
                with open(CACHE_LOC, "rb") as cachef:
                    return pickle.load(cachef)
            except:
                pass

        def get_new():
            return collections.defaultdict(list)

        results = collections.defaultdict(get_new)

        wb = load_workbook(filename=filename)
        for sheet in wb:
            values = list(sheet.values)
            headers = values[0]

            for row in values[1:]:
                row = dict(zip(headers, row))
                pk = row["CntryID"].upper(), row["PeriodID"].upper()
                results[pk][sheet.title].append(row)

        results = list(results.items())
        with open(CACHE_LOC, "wb") as cachef:
            pickle.dump(results, cachef)
        return results

    def handle(self, *args, **options):
        stream = logging.StreamHandler()
        stream.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s'
        ))
        logger.addHandler(stream)
        logger.setLevel(logging.WARNING)
        if int(options['verbosity']) > 0:
            logger.setLevel(logging.INFO)
        if int(options['verbosity']) > 1:
            logger.setLevel(logging.DEBUG)

        self.precision = options["precision"]

        try:
            # Create as the first admin we find.
            self.admin = User.objects.filter(is_superuser=True)[0]
        except Exception as e:
            logger.critical("Unable to find an admin: %s", e)
            return

        all_values = self.load_workbook(options["file"], use_cache=options["use_cache"])
        if options['limit']:
            all_values = all_values[:options['limit']]

        success_count = 0
        for pk, values_dict in all_values:
            logger.debug("Importing row %s", values_dict)

            try:
                party = self.parties[pk[0].upper()]
                period = self.periods[pk[1].upper()]
            except KeyError as e:
                logger.critical("Unable to find matching %s: %s", e, values_dict)
                break

            data = self.get_data(values_dict, party, period)
            self.check_consistency(data, party, period)
            if not options["dry_run"]:
                success_count += self.process_entry(party,
                                                    period,
                                                    data,
                                                    options["recreate"],
                                                    options["purge"])
        logger.info("Success on %s out of %s", success_count, len(all_values))
