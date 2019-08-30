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
    ObligationTypes,
    Meeting,
    Decision,
    ProcessAgentUsesReported,
    ProcessAgentApplication,
    ProcessAgentApplicationValidity,
    ProcessAgentContainTechnology,
    ProcessAgentEmissionLimit,
    ProcessAgentEmissionLimitValidity,
)
from ozone.core.models.utils import (
    float_to_decimal,
    float_to_decimal_zero_if_none,
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
        self.parties = {
            _party.abbr if _party.abbr != 'EU' else 'ECE': _party
            for _party in Party.objects.all()
        }
        self.substances = {_substance.substance_id: _substance
                           for _substance in Substance.objects.all()}
        self.meetings = {_meeting.meeting_id: _meeting
                         for _meeting in Meeting.objects.all()}
        self.wb = None
        self.admin = None
        self.contain_technologies_map = {}
        self.contain_technologies_objects_map = {}

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

        workbook_row_processors = [
            ('ProcAgentUsesValidity', self.process_pa_applications_validity),
            ('ProcAgentUses', self.process_pa_application),
            ('ProcAgentEmitLimitsValidity', self.process_pa_emission_limit_validity),
            ('ProcAgentEmitLimits', self.process_pa_emission_limit),
            ('ProcAgentContanTechnology', self.process_pa_contain_technology),
            ('ProcAgentUsesDateReported', self.process_submission_data),
            ('ProcAgentUsesReported', self.process_pa_uses_reported_data),
        ]
        worksheet_processors = {
            'ProcAgentContanTechnology': self.process_pa_contain_technology_ws,
        }
        if options["purge"]:
            workbook_row_processors = [
                ('ProcAgentUsesDateReported', self.process_submission_data),
                ('ProcAgentUsesReported', self.process_pa_uses_reported_data),
                ('ProcAgentContanTechnology', self.process_pa_contain_technology),
                ('ProcAgentUsesValidity', self.process_pa_applications_validity),
                ('ProcAgentEmitLimitsValidity', self.process_pa_emission_limit_validity),
            ]

        for workbook_name, workbook_processor in workbook_row_processors:
            worksheet = self.wb[workbook_name]
            values = list(worksheet.values)
            headers = values[0]
            if workbook_name in worksheet_processors:
                # This means that the whole worksheet data needs to be
                # pre-loaded
                worksheet_processors[workbook_name](values)
            for row in values[1:]:
                row = dict(zip(headers, row))
                workbook_processor(row, options["purge"])

    @staticmethod
    def _strip_description(description):
        return description.replace(" ", "").upper()

    def process_pa_contain_technology_ws(self, worksheet):
        """
        Loads all contain technology data in memory to populate submissions
        later.
        """
        headers = worksheet[0]
        for row in worksheet[1:]:
            row = dict(zip(headers, row))
            party = self.parties[row['CntryID']]
            period = self.periods[row['PeriodID']]
            description = row['ContainTechnology']

            key = (party, period)
            if (party, period) not in self.contain_technologies_map:
                self.contain_technologies_map[key] = set()
            self.contain_technologies_map[key].add(description)

    def process_submission_data(self, row, purge=False):
        try:
            return self._process_submission_data(row, purge)
        except KeyboardInterrupt:
            raise
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
                    _obligation_type=ObligationTypes.PROCAGENT.value
                ).first()
            )
            return

        submission = Submission.objects.filter(
            party_id=party,
            reporting_period_id=period,
            obligation___obligation_type=ObligationTypes.PROCAGENT.value,
        ).first()
        if not submission:
            entry = self.get_submission_data(
                party,
                period,
                row['DateReported'],
                "pa_uses_reported_remarks_secretariat",
                row['Remark']
            )
            submission = self.insert_submission(entry)

        # Add a single extra row for all contain technologies in this
        # submission
        ct_list = [
            self._strip_description(desc)
            for desc in self.contain_technologies_map.get((party, period), [])
        ]
        contain_technologies = [
            self.contain_technologies_objects_map[ct] for ct in ct_list
            if ct in self.contain_technologies_objects_map
        ]
        if contain_technologies:
            rep = ProcessAgentUsesReported.objects.create(
                submission=submission,
            )
            for tech in contain_technologies:
                rep.contain_technologies.add(tech)

    def process_pa_applications_validity(self, row, purge=False):
        try:
            return self._process_pa_applications_validity(row, purge)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(
                "Error %s while saving process agent uses validity for decision %",
                e, row['Decision']
            )

    @transaction.atomic
    def _process_pa_applications_validity(self, row, purge):
        decision = self.get_or_create_decision(row['Decision'])

        if purge:
            self.delete_pa_applications_validity(row)
            return

        if not getattr(decision, 'applications_validity', None):
            ProcessAgentApplicationValidity.objects.create(
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
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(
                "Error %s while saving process agent application for decision %s",
                e, row['Decision']
            )

    @transaction.atomic
    def _process_pa_application(self, row):
        decision = self.get_or_create_decision(row['Decision'])
        if getattr(decision, 'applications_validity', None):
            validity = decision.applications_validity
        else:
            if decision.decision_id == 'UNK':
                validity, created = ProcessAgentApplicationValidity.objects.get_or_create(
                    decision=decision
                )
            else:
                logger.error(
                    f"Uses validity does not exist for decision {decision}"
                )
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
        except KeyboardInterrupt:
            raise
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
        except KeyboardInterrupt:
            raise
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
            if decision.decision_id == 'UNK':
                validity, created = ProcessAgentEmissionLimitValidity.objects.get_or_create(
                    decision=decision
                )
            else:
                logger.error(
                    f"Limits validity does not exist for decision {decision}"
                )
                return

        party = self.parties[row['CntryID']]

        ProcessAgentEmissionLimit.objects.create(
            party=party,
            validity=validity,
            makeup_consumption=float_to_decimal_zero_if_none(
                row['MakeupOrCons']
            ),
            max_emissions=float_to_decimal_zero_if_none(row['MaxEmissions']),
            remark=row['Remark'] if row['Remark'] else ""
        )

        logger.info(
            f"Process agent emission limit for decision {decision} "
            f"and party {party.abbr} added."
        )

    def process_pa_uses_reported_data(self, row, purge=False):
        try:
            return self._process_pa_uses_reported_data(row, purge)
        except KeyboardInterrupt:
            raise
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
                    _obligation_type=ObligationTypes.PROCAGENT.value
                ).first()
            )
            return

        submission = self.get_or_create_submission(
            party,
            period,
            "pa_uses_reported_remarks_secretariat"
        )

        # There is a special case in ProcAgentUsesReported sheet, where there
        # are two decisions instead of one.
        for decision_id in row['Decision'].split(' AND '):
            decision = self.get_or_create_decision(decision_id)
            application = ProcessAgentApplication.objects.filter(
                counter=row['ProcessNumber'],
                validity__decision=decision
            ).first()
            ProcessAgentUsesReported.objects.create(
                submission=submission,
                decision=decision,
                application=application,
                makeup_quantity=float_to_decimal(row['MakeUpQuantity']),
                emissions=float_to_decimal(row['Emissions']),
                units=row['Units'],
                remark=row['Remarks'] if row['Remarks'] else "",
            )
            logger.info(
                f"Process agent uses reported for "
                f"{party.abbr}/{period.name} and decision {decision} added."
            )

    @transaction.atomic
    def get_or_create_decision(self, decision_id):
        if decision_id.endswith('-'):
            decision_id = decision_id[:-1]
        decision = Decision.objects.filter(decision_id=decision_id).first()
        if not decision:
            if decision_id == 'UNK':
                if 'UNK' in self.meetings:
                    meeting = self.meetings['UNK']
                else:
                    meeting, created = Meeting.objects.get_or_create(
                        meeting_id='UNK',
                        defaults={
                            'location': 'UNK',
                            'description': 'UNK'
                        }
                    )
                    self.meetings['UNK'] = meeting
            else:
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
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(
                "Error %s while saving process agent contain technology for %s/%s",
                e, row['CntryID'], row['PeriodID'],
                exc_info=True
            )
            return

    def _process_pa_contain_technology(self, row, purge):
        if purge:
            ProcessAgentContainTechnology.objects.filter(
                description=row['ContainTechnology']
            ).delete()
            logger.info(f"Process agent contain technology deleted.")
            return

        stripped_description = self._strip_description(row['ContainTechnology'])
        if stripped_description in self.contain_technologies_objects_map:
            logger.info(f"Process agent contain technology was already added.")
            return

        tech = ProcessAgentContainTechnology.objects.create(
            description=row['ContainTechnology']
        )
        self.contain_technologies_objects_map[stripped_description] = tech
        logger.info(f"Process agent contain technology added.")

    @transaction.atomic
    def get_or_create_submission(self, party, period, remark_name):
        submission = Submission.objects.filter(
            party_id=party,
            reporting_period_id=period,
            obligation___obligation_type=ObligationTypes.PROCAGENT.value,
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

        submission._current_state = "finalized"
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
                "_current_state": "finalized",
                "_previous_state": None,
                "flag_provisional": False,
                "flag_valid": True,
                "flag_superseded": False,
                "created_by_id": self.admin.id,
                "last_edited_by_id": self.admin.id,
                "obligation_id": Obligation.objects.filter(
                    _obligation_type=ObligationTypes.PROCAGENT.value
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
    def delete_pa_applications_validity(self, entry):
        obj = ProcessAgentApplicationValidity.objects.filter(
            decision__decision_id=entry['Decision'],
            start_date__year=entry['StartYear'],
            end_date__year=entry['EndYear']
        ).first()
        if obj:
            for related_data in ['pa_applications',]:
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
