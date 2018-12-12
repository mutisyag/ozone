"""Import Submission from Excel file.
"""
import logging

from django.core.management.base import BaseCommand
from django.db import transaction
from openpyxl import load_workbook

from ozone.core.models import User
from ozone.core.models import Party
from ozone.core.models import Submission
from ozone.core.models import SubmissionInfo
from ozone.core.models import ReportingPeriod
from ozone.core.models import Article7Questionnaire

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import Submission from Excel file"

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super().__init__(stdout=None, stderr=None, no_color=False)

        # Create as the first admin we find.
        self.admin_id = User.objects.filter(is_superuser=True)[0].id

        # Load all values in memory for faster lookups.
        self.current_submission = set(Submission.objects.filter(obligation_id=1).values_list(
            "party__abbr", "reporting_period__name"
        ))
        self.periods = {_period.name: _period for _period in ReportingPeriod.objects.all()}
        self.parties = {_party.abbr: _party for _party in Party.objects.all()}

        self.method = Submission.SubmissionMethods.LEGACY

    def add_arguments(self, parser):
        parser.add_argument('file',
                            help="the xlsx input file")
        parser.add_argument('--recreate', action="store_true", default=False,
                            help="Re-create if submission already exists.")
        parser.add_argument('--purge', action="store_true", default=False,
                            help="Purge all entries that were imported")

    def process_entry(self, *args, **kwargs):
        try:
            return self._process_entry(*args, **kwargs)
        except Exception as e:
            logger.error("Error %s while saving: %s", e, args[:2])
            return False

    def data_from_overall(self, row, party, period):
        return {
            "submission": {
                "schema_version": "legacy",
                "filled_by_secretariat": False,
                "created_at": row["DateCreate"],
                "updated_at": row["DateUpdate"],
                "version": 1,
                "_workflow_class": "default",
                "_current_state": "finalized",
                "_previous_state": None,
                "flag_provisional": False,
                "flag_valid": True,
                "flag_superseded": False,
                "submitted_via": self.method,
                "remarks_party": row["Remark"] or "",
                "remarks_secretariat": row["SubmissionType"] or "",
                "created_by_id": self.admin_id,
                "last_edited_by_id": self.admin_id,
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
                "date": row["DateReported"],
            },
            "art7": {
                "remarks_party": "",
                "remarks_os": "",
                "has_imports": row["Imported"],
                "has_exports": row["Exported"],
                "has_produced": row["Produced"],
                "has_destroyed": row["Destroyed"],
                "has_nonparty": row["NonPartyTrade"],
                "has_emissions": False,
                # "submission_id": "",
            },
            "art7_flags": {
                # TODO
            }
        }

    @transaction.atomic
    def _process_entry(self, party, period, values, recreate=False, purge=False):
        is_processed = (party.abbr, period.name) in self.current_submission
        if purge:
            Submission.objects.filter(
                party=party,
                reporting_period=period,
            ).delete()
            return True

        if is_processed:
            if recreate:
                Submission.objects.filter(
                    party=party,
                    reporting_period=period,
                ).delete()
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
        submission.call_transition("submit")
        submission.call_transition("process")
        submission.call_transition("finalize")
        return True

    def handle(self, *args, **options):
        stream = logging.StreamHandler()
        stream.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s'
        ))
        logger.addHandler(stream)
        logger.setLevel(logging.INFO)
        if int(options['verbosity']) > 1:
            logger.setLevel(logging.DEBUG)

        wb = load_workbook(filename=options['file'])
        values = list(wb["Overall"].values)
        headers = values[0]

        success_count = 0

        for row in values[1:]:
            row = dict(zip(headers, row))
            logger.debug("Importing row %s", row)

            try:
                party = self.parties[row["CntryID"]]
                period = self.periods[row["PeriodID"]]
            except KeyError as e:
                logger.critical("Unable to find matching %s: %s", e, row)
                break

            row_values = self.data_from_overall(row, party, period)
            success_count += self.process_entry(party,
                                                period,
                                                row_values,
                                                options["recreate"],
                                                options["purge"])
        logger.info("Success on %s out of %s", success_count, len(values) - 1)
