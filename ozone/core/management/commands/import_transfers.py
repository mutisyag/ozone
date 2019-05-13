import logging

from django.core.management.base import BaseCommand
from django.db import transaction
from openpyxl import load_workbook

from ozone.core.models import (
    Party,
    Substance,
    Submission,
    ReportingPeriod,
    Transfer,
    Obligation,
    User,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import transfers from Excel file"

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super().__init__(stdout=None, stderr=None, no_color=False)

        self.periods = {_period.name: _period
                        for _period in ReportingPeriod.objects.all()}
        self.parties = {_party.abbr: _party
                        for _party in Party.objects.all()}
        self.substances = {_substance.substance_id: _substance
                           for _substance in Substance.objects.all()}
        self.wb = None
        self.submissions_letters_map = {}

    def add_arguments(self, parser):
        parser.add_argument('file', help="the xlsx input file")
        parser.add_argument('--purge', action="store_true", default=False,
                            help="Purge all entries that were imported")

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

        try:
            # Create as the first admin we find.
            self.admin = User.objects.filter(is_superuser=True)[0]
        except Exception as e:
            logger.critical("Unable to find an admin: %s", e)
            return

        transfers_letters = self.load_workbook(options["file"])

        transfers_ws = self.wb['ProdTransfers']
        values = list(transfers_ws.values)
        headers = values[0]
        for row in values[1:]:
            row = dict(zip(headers, row))
            transfer_id = row['ProdTransferID']
            if not transfers_letters.get(transfer_id):
                logger.warning(
                    "Letter not found in ProdTransfersLetters sheet "
                    "for ProdTransferID=%s.",
                    transfer_id
                )
            self.process_data(
                row,
                transfers_letters[transfer_id] if transfers_letters.get(transfer_id) else None,
                options["purge"]
            )

    def load_workbook(self, filename):
        """
        Load the Excel file, collating letters data by ProdTransferID.

        Return a dictionary in the following format:
        {
            "ProdTransferID": {<letter-row>},
                ...
            }
        }
        """

        self.wb = load_workbook(filename=filename)

        ws_letters = self.wb['Letters']
        letters = {}
        values = list(ws_letters.values)
        headers = values[0]
        for row in values[1:]:
            row = dict(zip(headers, row))
            letters[row['LetterID']] = row

        ws_transfers_letters = self.wb['ProdTransfersLetters']
        result = {}
        values = list(ws_transfers_letters.values)
        headers = values[0]
        for row in values[1:]:
            row = dict(zip(headers, row))
            letter_id = row['LetterID']
            transfer_id = row['ProdTransferID']
            if not letters.get(letter_id):
                continue

            # Save data from first letter we found for this ProdTransferID.
            if not result.get(transfer_id):
                result[transfer_id] = letters[letter_id]

        return result

    def process_data(self, transfer, letter, purge=False):
        """
        Process the parsed data and insert it into the DB
        Only a wrapper, see _process_data.
        """
        try:
            return self._process_data(transfer, letter, purge)
        except Exception as e:
            logger.error(
                "Error %s while saving transfer %s", e, transfer['ProdTransferID'],
                exc_info=True
            )
            return 0

    @transaction.atomic
    def _process_data(self, transfer, letter, purge=False):
        party = self.parties[transfer['SrcCntryID']]
        period = self.periods[transfer['PeriodID']]
        obligation = Obligation.objects.get(id=4)

        if purge:
            self.delete_instance(party, period, obligation)
            return

        letter_id = letter['LetterID'] if letter else None
        map_key = (letter_id, party.abbr, period.name, obligation.id)
        if not letter or not self.submissions_letters_map.get(map_key):
            entry = self.get_submission_data(party, period, letter)
            submission = Submission.objects.create(
                **entry["submission"]
            )
            for key, value in entry["submission_info"].items():
                setattr(submission.info, key, value)
            submission.info.save()

            submission._current_state = "finalized"
            submission.save()

            # Fill aggregated data on submission import
            submission.fill_aggregated_data()

            for obj in submission.history.all():
                obj.history_user = self.admin
                obj.save()

            self.submissions_letters_map[map_key] = submission

            logger.info(
                "Submission %s/%s created.",
                party.abbr,
                period.name
            )
        submission = self.submissions_letters_map[map_key]

        # Little hack to allow modifications on this submission
        submission._current_state = "data_entry"
        submission.save()

        # Fill aggregated data on submission import
        submission.fill_aggregated_data()

        transfer = self.get_transfer_data(transfer)
        Transfer.objects.create(
            submission=submission,
            **transfer
        )

        # Set current_state back to finalized
        submission._current_state = "finalized"
        submission.save()

        logger.info(
            "Transfer added to %s/%s submission.",
            party.abbr,
            period.name
        )

    def get_submission_data(self, party, period, letter):
        letter_date = letter["LetterDate"] if letter else None
        if letter:
            transfers_remarks_secretariat = letter["LetterDate"].strftime("%m/%d/%Y") + "\n"
            transfers_remarks_secretariat += letter["LetterSubject"] + "\n"
            transfers_remarks_secretariat += letter["Remarks"] if letter["Remarks"] else ""
        else:
            transfers_remarks_secretariat = ""
        return {
            "submission": {
                "schema_version": "legacy",
                "created_at": letter_date,
                "updated_at": letter_date,
                "submitted_at": letter_date,
                "version": 1,
                "_workflow_class": "default",
                "_current_state": "finalized",
                "_previous_state": None,
                "flag_provisional": False,
                "flag_valid": True,
                "flag_superseded": False,
                "created_by_id": self.admin.id,
                "last_edited_by_id": self.admin.id,
                "obligation_id": 4,
                "party_id": party.id,
                "reporting_period_id": period.id,
                "cloned_from_id": None,
                "transfers_remarks_secretariat": transfers_remarks_secretariat,
            },
            "submission_info": {
                "reporting_officer": "",
                "designation": "",
                "organization": "",
                "postal_address": "",
                "country": party.name,
                "phone": "",
                "email": "",
                "date": letter_date,
            },
            "transfers": []
        }

    def get_transfer_data(self, transfer):
        substance = self.substances.get(transfer["SubstID"])
        destination_party = self.parties[transfer['DestCntryID']]

        return {
            "substance_id": substance.id,
            "transferred_amount": transfer["ProdTransfer"],
            "is_basic_domestic_need": transfer['IsBDN'],
            "destination_party_id": destination_party.id,
            "remarks_os": transfer["Remark"] if transfer["Remark"] else ""
        }

    def delete_instance(self, party, period, obligation):
        """
        Removes the submission identified by the party, period and obligation
        and any related data.
        """

        qs = Submission.objects.filter(
            party=party,
            reporting_period=period,
            obligation=obligation
        ).all()

        for sub in qs:
            logger.info("Deleting submission %s/%s", party.abbr, period.name)
            sub._current_state = 'data_entry'
            sub.save()
            for related_data in sub.RELATED_DATA:
                for instance in getattr(sub, related_data).all():
                    logger.debug("Deleting related data: %s", instance)
                    instance.delete()
            sub.__class__.data_changes_allowed = True
            sub.delete()
