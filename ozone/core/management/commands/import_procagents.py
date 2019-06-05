import logging

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from openpyxl import load_workbook

from ozone.core.models import (
    Party,
    Substance,
    Submission,
    ReportingPeriod,
    User,
    Obligation,
    FormTypes,
    ProcessAgentUsesReported,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = _(
        "Import Process Agents - uses, reports & related tables from Excel file"
    )

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super().__init__(stdout=None, stderr=None, no_color=False)

        self.periods = {_period.name: _period
                        for _period in ReportingPeriod.objects.all()}
        self.parties = {_party.abbr: _party
                        for _party in Party.objects.all()}
        self.substances = {_substance.substance_id: _substance
                           for _substance in Substance.objects.all()}

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
            ('ProcAgentUsesDateReported', self.process_submission_data),
            ('ProcAgentUsesReported', self.process_pa_uses_reported_data)
        ]

        # First populated submissions using ProcAgentUsesDateReported sheet
        for workbook_name, workbook_processor in workbook_processors:
            worksheet = self.wb[workbook_name]
            values = list(worksheet.values)
            headers = values[0]
            for row in values[1:]:
                row = dict(zip(headers, row))
                workbook_processor(row, options["purge"])

    def process_submission_data(self, row, purge=False):
        try:
            return self._process_submission_data(row, purge)
        except Exception as e:
            logger.error(
                "Error %s while saving submission %s/%s", e, row['CntryID'], row['PeriodID'],
                exc_info=True
            )
            return 0

    def _process_submission_data(self, row, purge):
        party = self.parties[row['CntryID']]
        period = self.periods[row['PeriodID']]
        submission = Submission.objects.filter(
            party_id=party,
            reporting_period_id=period,
            obligation___form_type=FormTypes.PROCAGENT.value,
        ).first()

        if purge:
            self.delete_instance(
                party,
                period,
                Obligation.objects.filter(_form_type=FormTypes.PROCAGENT.value).first()
            )
        elif not submission:
            entry = self.get_submission_data(
                party,
                period,
                row['DateReported'],
                row['Remark']
            )
            self.insert_submission(entry)

    def process_pa_uses_reported_data(self, row, purge):
        try:
            return self._process_pa_uses_reported_data(row, purge)
        except Exception as e:
            logger.error(
                "Error %s while saving the reported uses of process agent for %s/%s",
                e, row['Party'], row['PeriodID'],
                exc_info=True
            )
            return 0

    @transaction.atomic
    def _process_pa_uses_reported_data(self, row, purge):
        party = self.parties[row['Party']]
        period = self.periods[row['PeriodID']]
        submission = Submission.objects.filter(
            party_id=party,
            reporting_period_id=period,
            obligation___form_type=FormTypes.PROCAGENT.value,
        ).first()

        if purge:
            self.delete_instance(
                party,
                period,
                Obligation.objects.filter(_form_type=FormTypes.PROCAGENT.value).first()
            )
            return

        if not submission:
            entry = self.get_submission_data(
                party,
                period,
                None,
                _(
                    "Submission for this party and period "
                    "not found in ProcAgentUsesDateReported"
                )
            )
            submission = self.insert_submission(entry)

        entry = self.get_pa_uses_reported_data(row)
        ProcessAgentUsesReported.objects.create(
            **entry,
            submission=submission
        )
        logger.info(f"Process agent uses reported added.")

    @transaction.atomic
    def insert_submission(self, entry):
        submission = Submission.objects.create(
            **entry["submission"]
        )
        for key, value in entry["submission_info"].items():
            setattr(submission.info, key, value)
        submission.info.save()

        submission._current_state = "submitted"
        submission.save()

        for obj in submission.history.all():
            obj.history_user = self.admin
            obj.save()

        logger.info(
            f"Submission for {submission.party}/"
            f"{submission.reporting_period} created."
        )

        return submission

    def get_submission_data(self, party, period, date_reported, remark):
        return {
            "submission": {
                "schema_version": "legacy",
                "submitted_at": date_reported,
                "version": 1,
                "_workflow_class": "default_process_agent",
                "_current_state": "submitted",
                "_previous_state": None,
                "flag_provisional": False,
                "flag_valid": True,
                "flag_superseded": False,
                "created_by_id": self.admin.id,
                "last_edited_by_id": self.admin.id,
                "obligation_id": Obligation.objects.filter(
                    _form_type=FormTypes.PROCAGENT.value
                ).first().id,
                "party_id": party.id,
                "reporting_period_id": period.id,
                "cloned_from_id": None,
                "pa_uses_reported_remarks": remark,
            },
            "submission_info": {
                "reporting_officer": "",
                "designation": "",
                "organization": "",
                "postal_address": "",
                "country_id": party.id,
                "phone": "",
                "email": "",
                "date": date_reported,
            },
        }

    def get_pa_uses_reported_data(self, row):
        return {
            "decision": row['Decision'],
            "process_number": row['ProcessNumber'],
            "makeup_quantity": row['MakeUpQuantity'],
            "emissions": row['Emissions'],
            "units": row['Units'],
            "remark": row['Remarks'] if row['Remarks'] else ""
        }

    @transaction.atomic
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
