import logging

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import make_aware

from openpyxl import load_workbook

from ozone.core.models import (
    Party,
    Substance,
    Submission,
    ReportingPeriod,
    Transfer,
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
        self.transfers_map = {}

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

        # Load all the data.
        self.wb = load_workbook(filename=options["file"])

        workbook_processors = [
            ('Letters', self.process_letter_data),
            ('ProdTransfers', self.process_transfer_data),
            ('ProdTransfersLetters', self.process_letter_transfer_data),
        ]
        if options["purge"]:
            workbook_processors = reversed(workbook_processors)

        # Process & populate letters, transfers, and then transfer's letters
        for workbook_name, workbook_processor in workbook_processors:
            worksheet = self.wb[workbook_name]
            values = list(worksheet.values)
            headers = values[0]
            for row in values[1:]:
                row = dict(zip(headers, row))
                workbook_processor(row, options["purge"])

    def process_letter_data(self, letter, purge=False):
        try:
            return self._process_letter_data(letter, purge)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(
                "Error %s while saving transfer %s", e, letter['LetterID'],
                exc_info=True
            )
            return 0

    @transaction.atomic
    def _delete_letter_instance(self, letter_id, entry):
        sub = entry["submission"]
        submission = Submission.objects.filter(
            party_id=sub["party_id"],
            reporting_period_id=sub["reporting_period_id"],
            obligation_id=sub["obligation_id"],
        ).first()
        if submission:
            logger.info(f"Deleting letter {letter_id}")
            submission._current_state = 'data_entry'
            submission.save()
            submission.delete()
        else:
            logger.info(f"Letter {letter_id} not found in database.")

    @transaction.atomic
    def _process_letter_data(self, letter, purge=False):
        letter_id = letter['LetterID'] if letter else None
        entry = self.get_submission_data(letter)

        if purge:
            self._delete_letter_instance(letter_id, entry)
            return

        if not self.submissions_letters_map.get(letter_id):
            submission = Submission.objects.create(
                **entry["submission"]
            )
            for key, value in entry["submission_info"].items():
                setattr(submission.info, key, value)
            submission.info.save()

            submission._current_state = "finalized"
            submission.save()

            # Setting updated_at and created_at like this avoids creating a new
            # history item.
            if entry["submission"]["created_at"]:
                Submission.objects.filter(pk=submission.pk).update(
                    created_at=entry["submission"]["created_at"]
                )
            if entry["submission"]["updated_at"]:
                Submission.objects.filter(pk=submission.pk).update(
                    updated_at=entry["submission"]["updated_at"]
                )
            for obj in submission.history.all():
                obj.history_user = self.admin
                obj.created_at = entry["submission"]["created_at"]
                obj.updated_at = entry["submission"]["updated_at"]
                obj.history_date = entry["submission"]["created_at"]
                obj.save()

            self.submissions_letters_map[letter_id] = submission

            logger.info(
                f"Submission for {submission.party}/"
                f"{submission.reporting_period} created."
            )

    def process_transfer_data(self, transfer, purge=False):
        """
        Process the parsed data and insert it into the DB
        Only a wrapper, see _process_transfer_data.
        """
        try:
            return self._process_transfer_data(transfer, purge)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(
                f"Error {e} while saving transfer {transfer['ProdTransferID']}",
                exc_info=True
            )
            return 0

    @transaction.atomic
    def _delete_transfer_instance(self, transfer_id, entry):
        transfer = Transfer.objects.filter(
            reporting_period__id=entry["reporting_period_id"],
            substance_id=entry["substance_id"],
            transfer_type="P",
            transferred_amount=entry["transferred_amount"],
            is_basic_domestic_need=entry["is_basic_domestic_need"],
            source_party_id=entry["source_party_id"],
            destination_party_id=entry["destination_party_id"]
        ).first()
        if transfer:
            logger.info(f"Deleting transfer {transfer_id}")
            transfer.delete()
        else:
            logger.info(f"Transfer {transfer_id} not found in database.")

    @transaction.atomic
    def _process_transfer_data(self, transfer, purge=False):
        transfer_id = transfer['ProdTransferID']
        entry = self.get_transfer_data(transfer)

        if purge:
            self._delete_transfer_instance(transfer_id, entry)
            return

        if not self.transfers_map.get(transfer_id):
            t = Transfer.objects.create(
                **entry
            )
            # Fill aggregated data based on this transfer
            t.populate_aggregated_data()

            self.transfers_map[transfer_id] = t

            logger.info(f"Transfer {transfer_id} added")

    def process_letter_transfer_data(self, entry, purge=False):
        """
        Process the parsed data and insert it into the DB
        Only a wrapper, see _process_letter_transfer_data.
        """
        try:
            return self._process_letter_transfer_data(entry, purge)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(
                "Error %s while processing transfer-letter mapping %s %s", e,
                entry['ProdTransferID'], entry['LetterID'],
                exc_info=True
            )
            return 0

    @transaction.atomic
    def _process_letter_transfer_data(self, entry, purge=False):
        if purge:
            # Nothing to be done here
            return

        transfer = self.transfers_map.get(entry['ProdTransferID'], None)
        submission = self.submissions_letters_map.get(entry['LetterID'], None)

        if not transfer or not submission:
            logger.info(
                f"Could not process mapping of letter {entry['LetterID']} and "
                f"transfer {entry['ProdTransferID']}"
            )
            return

        # Set the submission on the transfer
        if transfer.source_party == submission.party:
            transfer.source_party_submission = submission
        elif transfer.destination_party == submission.party:
            transfer.destination_party_submission = submission

        transfer.save()

    def get_submission_data(self, letter):
        letter_date = letter["LetterDate"] if letter else None
        letter_date = make_aware(letter_date) if letter_date else None
        if letter:
            transfers_remarks_secretariat = letter["LetterDate"].strftime("%m/%d/%Y") + "\n"
            transfers_remarks_secretariat += letter["LetterSubject"] + "\n"
            transfers_remarks_secretariat += letter["Remarks"] if letter["Remarks"] else ""
        else:
            transfers_remarks_secretariat = ""
        party = self.parties[letter['LetterSenderCntryID']]
        period = self.periods[letter['LetterDate'].strftime("%Y")]

        return {
            "submission": {
                "schema_version": "legacy",
                "created_at": letter_date,
                "updated_at": letter_date,
                "submitted_at": letter_date,
                "version": 1,
                "_workflow_class": "default_transfer",
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
                "country_id": party.id,
                "phone": "",
                "email": "",
                "date": letter_date,
            },
        }

    def get_transfer_data(self, transfer):
        substance = self.substances.get(transfer["SubstID"])
        destination_party = self.parties[transfer['DestCntryID']]
        source_party = self.parties[transfer['SrcCntryID']]
        reporting_period = self.periods[transfer['PeriodID']]

        return {
            "reporting_period_id": reporting_period.id,
            "substance_id": substance.id,
            "transfer_type": "P",
            "transferred_amount": transfer["ProdTransfer"],
            "is_basic_domestic_need": transfer['IsBDN'],
            "source_party_id": source_party.id,
            "destination_party_id": destination_party.id,
            "source_party_submission": None,
            "destination_party_submission": None,
            #"remarks_os": transfer["Remark"] if transfer["Remark"] else ""
        }
