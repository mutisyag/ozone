from datetime import date
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
    Meeting,
    Decision,
    ProcessAgentUsesReported,
    ProcessAgentUsesValidity,
    ProcessAgentEmissionLimitValidity,
    ProcessAgentApplication,
    ProcessAgentContainTechnology,
    ProcessAgentEmissionLimit,
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
        self.meetings = {_meeting.meeting_id: _meeting
                         for _meeting in Meeting.objects.all()}

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
            ('ProcAgentUsesValidity', self.process_pa_uses_validity),
            ('ProcAgentUses', self.process_pa_application),
            ('ProcAgentEmitLimitsValidity', self.process_pa_emission_limit_validity),
            ('ProcAgentEmitLimits', self.process_pa_emission_limit),
            ('ProcAgentUsesDateReported', self.process_submission_data),
            ('ProcAgentUsesReported', self.process_pa_uses_reported_data),
            ('ProcAgentContanTechnology', self.process_pa_contain_technology)
        ]
        if options["purge"]:
            workbook_processors = [
                ('ProcAgentUsesDateReported', self.process_submission_data),
                ('ProcAgentUsesReported', self.process_pa_uses_reported_data),
                ('ProcAgentContanTechnology', self.process_pa_contain_technology),
                ('ProcAgentUsesValidity', self.process_pa_uses_validity),
                ('ProcAgentEmitLimitsValidity', self.process_pa_emission_limit_validity),
            ]

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
            return

    @transaction.atomic
    def _process_submission_data(self, row, purge):
        party = self.parties[row['CntryID']]
        period = self.periods[row['PeriodID']]

        if purge:
            self.delete_submission(
                party,
                period,
                Obligation.objects.filter(
                    _form_type=FormTypes.PROCAGENT.value
                ).first()
            )
            return

        submission = Submission.objects.filter(
            party_id=party,
            reporting_period_id=period,
            obligation___form_type=FormTypes.PROCAGENT.value,
        ).first()
        if not submission:
            entry = self.get_submission_data(
                party,
                period,
                row['DateReported'],
                "pa_uses_reported_remarks_secretariat",
                row['Remark']
            )
            self.insert_submission(entry)

    def process_pa_uses_validity(self, row, purge=False):
        try:
            return self._process_pa_uses_validity(row, purge)
        except Exception as e:
            logger.error(
                "Error %s while saving process agent uses validity for decision %",
                e, row['Decision']
            )

    @transaction.atomic
    def _process_pa_uses_validity(self, row, purge):
        decision = self.get_or_create_decision(row['Decision'])

        if purge:
            self.delete_pa_uses_validity(row)
            return

        if not getattr(decision, 'uses_validity', None):
            ProcessAgentUsesValidity.objects.create(
                decision=decision,
                start_date=date(row['StartYear'], 1, 1) if row['StartYear'] else None,
                end_date=date(row['EndYear'], 12, 31) if row['EndYear'] else None
            )
            logger.info(
                f"Process agent uses validity for decision {decision} added."
            )
        else:
            logger.info(
                f"Process agent uses validity for decision {decision} already exists."
            )

    def process_pa_application(self, row, purge=False):
        try:
            return self._process_pa_application(row)
        except Exception as e:
            logger.error(
                "Error %s while saving process agent application for decision %s",
                e, row['Decision']
            )

    @transaction.atomic
    def _process_pa_application(self, row):
        decision = self.get_or_create_decision(row['Decision'])
        if getattr(decision, 'uses_validity', None):
            validity = decision.uses_validity
        else:
            logger.error(f"Uses validity does not exists decision {decision}")
            return

        ProcessAgentApplication.objects.create(
            validity=validity,
            counter=int(row['Counter']),
            substance=self.substances[row['SubstID']],
            application=row['Application'],
            remark=row['Remark'] if row['Remark'] else ""
        )
        logger.info(f"Process agent application for decision {decision} added.")

    def process_pa_emission_limit_validity(self, row, purge=False):
        try:
            return self._process_pa_emission_limit_validity(row, purge)
        except Exception as e:
            logger.error(
                "Error %s while saving process agent emission limits validity for decision %s",
                e, row['Decision']
            )

    @transaction.atomic
    def _process_pa_emission_limit_validity(self, row, purge):
        if purge:
            self.delete_pa_emission_limit_validity(row)
            return

        decision = self.get_or_create_decision(row['Decision'])

        if not getattr(decision, 'limits_validity', None):
            ProcessAgentEmissionLimitValidity.objects.create(
                decision=decision,
                start_date=date(row['StartYear'], 1, 1) if row['StartYear'] else None,
                end_date=date(row['EndYear'], 12, 31) if row['EndYear'] else None
            )
            logger.info(
                f"Process agent emission limits validity "
                f"for decision {decision} added."
            )
        else:
            logger.info(
                f"Process agent emission limits validity "
                f"for decision {decision} already exists."
            )

    def process_pa_emission_limit(self, row, purge=False):
        try:
            return self._process_pa_emission_limit(row)
        except Exception as e:
            logger.error(
                "Error %s while saving process agent emission limit "
                "for party %s and decision %s",
                e, row['CntryID'], row['Decision'],
                exc_info=True
            )
            return

    @transaction.atomic
    def _process_pa_emission_limit(self, row):
        decision = self.get_or_create_decision(row['Decision'])
        if getattr(decision, 'limits_validity', None):
            validity = decision.limits_validity
        else:
            logger.error(f"Limits validity does not exists decision {decision}")
            return

        party = self.parties[row['CntryID']]

        ProcessAgentEmissionLimit.objects.create(
            party=party,
            validity=validity,
            makeup_consumption=row['MakeupOrCons'],
            max_emissions=row['MaxEmissions'],
            remark=row['Remark'] if row['Remark'] else ""
        )

        logger.info(
            f"Process agent emission limit for decision {decision} "
            f"and party {party.abbr} added."
        )

    def process_pa_uses_reported_data(self, row, purge=False):
        try:
            return self._process_pa_uses_reported_data(row, purge)
        except Exception as e:
            logger.error(
                "Error %s while saving the reported uses of process agent for %s/%s",
                e, row['Party'], row['PeriodID'],
                exc_info=True
            )
            return

    @transaction.atomic
    def _process_pa_uses_reported_data(self, row, purge):
        party = self.parties[row['Party']]
        period = self.periods[row['PeriodID']]

        if purge:
            self.delete_submission(
                party,
                period,
                Obligation.objects.filter(
                    _form_type=FormTypes.PROCAGENT.value
                ).first()
            )
            return

        submission = self.get_or_create_submission(
            party,
            period,
            "pa_uses_reported_remarks_secretariat"
        )

        decision = self.get_or_create_decision(row['Decision'])
        if getattr(decision, 'uses_validity', None):
            validity = decision.uses_validity
        else:
            logger.error(f"Uses validity does not exists decision {decision}")
            return

        ProcessAgentUsesReported.objects.create(
            submission=submission,
            validity=validity,
            process_number=row['ProcessNumber'],
            makeup_quantity=row['MakeUpQuantity'],
            emissions=row['Emissions'],
            units=row['Units'],
            remark=row['Remarks'] if row['Remarks'] else "",
        )
        logger.info(
            f"Process agent uses reported for {party.abbr}/{period.name} "
            f"and decision {decision} added."
        )

    @transaction.atomic
    def get_or_create_decision(self, decision_id):
        decision = Decision.objects.filter(decision_id=decision_id).first()
        if not decision:
            meeting_id = decision_id.split('/')[0]
            meeting = self.meetings[meeting_id]
            decision = Decision.objects.create(
                decision_id=decision_id,
                meeting=meeting
            )
            logger.info(f"Decision {decision_id} added.")
        return decision

    def process_pa_contain_technology(self, row, purge=False):
        try:
            return self._process_pa_contain_technology(row, purge)
        except Exception as e:
            logger.error(
                "Error %s while saving process agent contain technology for %s/%s",
                e, row['CntryID'], row['PeriodID'],
                exc_info=True
            )
            return

    def _process_pa_contain_technology(self, row, purge):
        party = self.parties[row['CntryID']]
        period = self.periods[row['PeriodID']]

        if purge:
            self.delete_submission(
                party,
                period,
                Obligation.objects.filter(
                    _form_type=FormTypes.PROCAGENT.value
                ).first()
            )
            return

        submission = self.get_or_create_submission(
            party,
            period,
            "pa_contain_technology_remarks_secretariat"
        )

        ProcessAgentContainTechnology.objects.create(
            submission=submission,
            contain_technology=row['ContainTechnology']
        )
        logger.info(f"Process agent contain technology added.")

    @transaction.atomic
    def get_or_create_submission(self, party, period, remark_name):
        submission = Submission.objects.filter(
            party_id=party,
            reporting_period_id=period,
            obligation___form_type=FormTypes.PROCAGENT.value,
        ).first()
        if not submission:
            entry = self.get_submission_data(
                party,
                period,
                None,
                remark_name,
                _(
                    "Submission for this party and period "
                    "not found in ProcAgentUsesDateReported"
                )
            )
            submission = self.insert_submission(entry)
        return submission

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

    def get_submission_data(self, party, period, date_reported, remark_name, remark_val):
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
                remark_name: remark_val,
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

    @transaction.atomic
    def delete_submission(self, party, period, obligation):
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
            for related_data, aggr_flag in sub.RELATED_DATA:
                for instance in getattr(sub, related_data).all():
                    logger.info("Deleting related data: %s", instance)
                    instance.delete()
            sub.__class__.data_changes_allowed = True
            sub.delete()

    @transaction.atomic
    def delete_pa_uses_validity(self, entry):
        obj = ProcessAgentUsesValidity.objects.filter(
            decision__decision_id=entry['Decision'],
            start_date__year=entry['StartYear'],
            end_date__year=entry['EndYear']
        ).first()
        if obj:
            for related_data in ['pa_applications', 'pa_uses_reported']:
                for instance in getattr(obj, related_data).all():
                    logger.info("Deleting related data: %s", instance)
                    instance.delete()
            obj.delete()
            logger.info(
                f"Process agent uses validity for {entry['Decision']} deleted."
            )
        else:
            logger.info(
                f"Process agent uses validity for {entry['Decision']} "
                f"not found in database."
            )

    @transaction.atomic
    def delete_pa_emission_limit_validity(self, entry):
        obj = ProcessAgentEmissionLimitValidity.objects.filter(
            decision__decision_id=entry['Decision'],
            start_date__year=entry['StartYear'],
            end_date__year=entry['EndYear']
        ).first()
        if obj:
            for instance in getattr(obj, 'pa_emission_limits').all():
                logger.info("Deleting related data: %s", instance)
                instance.delete()
            obj.delete()
            logger.info(
                f"Process agent emission limit validity "
                f"for {entry['Decision']} deleted."
            )
        else:
            logger.info(
                f"Process agent emission limit validity "
                f"for {entry['Decision']} not found in database."
            )
