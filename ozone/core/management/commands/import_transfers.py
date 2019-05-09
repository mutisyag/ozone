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
        self.total_submissions = 0

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

        data = self.load_workbook(options["file"])

        try:
            # Create as the first admin we find.
            self.admin = User.objects.filter(is_superuser=True)[0]
        except Exception as e:
            logger.critical("Unable to find an admin: %s", e)
            return

        success_count = 0
        for letter_id in data.keys():
            success_count += self.process_data(
                data[letter_id],
                letter_id,
                purge=options["purge"]
            )
        logger.info("Success on %s out of %s", success_count, self.total_submissions)

    def load_workbook(self, filename):
        """Loads the Excel file, collating the data based on the
        LetterID and ProdTransferID.

        Return a dictionary in the following format:
        {
            "LetterID": {
                "letter": {<letter-row>},
                "transfers": {
                    "ProdTransferID_1": {<transfer-row>},
                    "ProdTransferID_2": {<transfer-row>},
                    ...
                }
            }
        }
        """

        wb = load_workbook(filename=filename)

        ws_letters = wb['Letters']
        letters = {}
        values = list(ws_letters.values)
        headers = values[0]
        for row in values[1:]:
            row = dict(zip(headers, row))
            letters[row['LetterID']] = row

        ws_transfers = wb['ProdTransfers']
        transfers = {}
        values = list(ws_transfers.values)
        headers = values[0]
        for row in values[1:]:
            row = dict(zip(headers, row))
            transfers[row['ProdTransferID']] = row

        ws_transfers_letters = wb['ProdTransfersLetters']
        result = {}
        values = list(ws_transfers_letters.values)
        headers = values[0]
        for row in values[1:]:
            row = dict(zip(headers, row))
            letter_id = row['LetterID']
            transfer_id = row['ProdTransferID']
            if not letters.get(letter_id):
                logger.warning("LetterID %s not found in Letters sheet, skipping.", letter_id)
                continue
            if not transfers.get(transfer_id):
                logger.warning("ProdTransferID %s not found in ProdTransfers sheet, skipping.", transfer_id)
                continue
            if not result.get(letter_id):
                result[letter_id] = {}
                result[letter_id]['transfers'] = {}
            result[letter_id]['letter'] = letters[letter_id]
            result[letter_id]['transfers'][transfer_id] = transfers[transfer_id]

        return result

    def get_data(self, data):
        """
        data is a dictionary in the following format:
        {
            "letter": {<letter-row>},
            "transfers": {
                "ProdTransferID_1": {<transfer-row>},
                "ProdTransferID_2": {<transfer-row>},
                ...
        }
        Parse this dictionary to return a list of submissions (if there are
        multiple periods) that matches our models.
        """

        party_abbr = data['letter']['LetterSenderCntryID'].upper()
        party = self.parties[party_abbr]

        transfers_by_periods = self.get_transfers_by_periods(data['transfers'])

        result = []
        for period_name, transfers in transfers_by_periods.items():
            period = self.periods[period_name]
            letter_date = data["letter"]["LetterDate"]
            result.append({
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
                    "transfers_remarks_secretariat": data["letter"]["Remarks"] if data["letter"]["Remarks"] else "",
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
                "transfers": self.get_transfers(transfers, party_abbr)
            })
            self.total_submissions += 1
        return result

    def get_transfers_by_periods(self, transfers):
        """
        Group by period every transfer row.
        Returns a dictionary in the following format:
        {
            "period1": [{<transfer-row>}, {<transfer-row>}, ... ],
            "period2": [{<transfer-row>}, {<transfer-row>}, ... ],
            ...
        }
        """

        result = {}
        for transfer in transfers.values():
            if not result.get(transfer['PeriodID']):
                result[transfer['PeriodID']] = []
            result[transfer['PeriodID']].append(transfer)
        return result

    def get_transfers(self, transfers, letter_sender_party):
        result = []
        for transfer in transfers:
            substance = self.substances.get(transfer["SubstID"])
            if transfer["SrcCntryID"] == letter_sender_party:
                destination_party = self.parties[transfer['DestCntryID']]
            else:
                destination_party = self.parties[transfer['SrcCntryID']]

            result.append({
                "transfer_type": "P",
                "substance_id": substance.id,
                "transferred_amount": transfer["ProdTransfer"],
                "is_basic_domestic_need": transfer['IsBDN'],
                "destination_party": destination_party,
                "remarks_os": transfer["Remark"] if transfer["Remark"] else ""
            })
        return result

    def process_data(self, data, letter_id, purge=False):
        """
        Process the parsed data and insert it into the DB
        Only a wrapper, see _process_data.
        """
        try:
            return self._process_data(
                data,
                purge=purge
            )
        except Exception as e:
            logger.error(
                "Error %s while saving letter %s", e, letter_id,
                exc_info=True
            )
            return 0

    @transaction.atomic
    def _process_data(self, data, purge=False):
        entries = self.get_data(data)

        success_count = 0
        if purge:
            for entry in entries:
                success_count += self.delete_instance(
                    party=Party.objects.get(id=entry['submission']['party_id']),
                    period=ReportingPeriod.objects.get(id=entry['submission']['reporting_period_id']),
                    obligation=Obligation.objects.get(id=4)
                )
            return success_count

        for entry in entries:
            import pdb; pdb.set_trace()
            submission = Submission.objects.create(
                **entry["submission"]
            )

            for key, value in entry["submission_info"].items():
                setattr(submission.info, key, value)
            submission.info.save()

            for val in entry["transfers"]:
                Transfer.objects.create(
                    submission=submission,
                    **val
                )

            submission._current_state = "finalized"
            submission.save()

            # TODO Fill aggregated data

            for obj in submission.history.all():
                obj.history_user = self.admin
                obj.save()

            logger.info(
                "Submission %s/%s imported.",
                Party.objects.get(id=entry['submission']['party_id']).abbr,
                ReportingPeriod.objects.get(id=entry['submission']['reporting_period_id']).name
            )
            success_count += 1

        return success_count

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

        return qs.count()
