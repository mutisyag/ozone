import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction

from openpyxl import load_workbook

from ozone.core.models import (
    Decision,
    Meeting,
    Party,
    ReportingPeriod,
    Group,
    PlanOfActionDecision,
    PlanOfAction,
)


User = get_user_model()


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import plans of actions and decisions."

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super().__init__(stdout=None, stderr=None, no_color=False)

        self.periods = {
            _period.name: _period.id
            for _period in ReportingPeriod.objects.all()
        }
        self.parties = {
            _party.abbr: _party.id
            for _party in Party.objects.all()
        }
        self.groups = {
            _group.group_id: _group.id
            for _group in Group.objects.all()
        }
        self.meetings = {
            _meeting.meeting_id: _meeting
            for _meeting in Meeting.objects.all()
        }
        self.decisions = {}
        self.admin = None

    def add_arguments(self, parser):
        parser.add_argument(
            'file',
            help="the xlsx input file"
        )
        parser.add_argument(
            '--purge', action="store_true", default=False,
            help="Purge all entries that were imported"
        )

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

        wb = load_workbook(filename=options["file"])

        worksheet_processors = [
            ("Plans_of_Action_Decs", self.import_decision_data),
            ("Plans_of_Action", self.import_plan_data),
        ]
        if options["purge"]:
            worksheet_processors = reversed(worksheet_processors)
        for ws_name, ws_processor in worksheet_processors:
            sheet = wb[ws_name]
            values = list(sheet.values)
            headers = values[0]
            for row in values[1:]:
                row = dict(zip(headers, row))
                ws_processor(row, options["purge"])

    def import_decision_data(self, row, purge=False):
        try:
            return self._import_decision_data(row, purge)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(
                f"Error {e} while saving plan of action decision "
                f"with ID {row['DecID']}",
                exc_info=True
            )
            return

    @transaction.atomic
    def get_or_create_decision(self, decision_id):
        if decision_id.endswith('-'):
            decision_id = decision_id[:-1]
        decision = Decision.objects.filter(decision_id=decision_id).first()
        if not decision:
            meeting_id = decision_id.split('/')[0]
            meeting = self.meetings.get(meeting_id, None)
            if meeting is None:
                logger.error(
                    f"Error when importing decision {decision_id}: "
                    f"meeting {meeting_id} does not exist."
                )
                return
            decision = Decision.objects.create(
                decision_id=decision_id,
                meeting=meeting
            )
            logger.info(f"Decision {decision_id} added.")
        return decision

    @transaction.atomic
    def _import_decision_data(self, row, purge):
        decision_id = row["Decision"]
        decision = self.get_or_create_decision(decision_id)
        create_data = {
            "decision_id": decision.id,
            "party_id": self.parties[row["CntryID"]],
            "year_adopted": int(row["YearAdopted"]),
        }
        if purge:
            PlanOfActionDecision.objects.filter(
                **create_data
            ).delete()
            logger.info(f"Deleted plan of action decision {row['DecID']}")
            return

        dec = PlanOfActionDecision.objects.create(**create_data)
        self.decisions[row["DecID"]] = dec
        logger.info(f"Created plan of action decision {row['DecID']}")

    def import_plan_data(self, row, purge=False):
        try:
            return self._import_plan_data(row, purge)
        except KeyboardInterrupt:
            raise
        except ValidationError as e:
            logger.error(
                f"Error {e} while saving plan of action for "
                f"{row['CntryID']} - {row['PeriodID']} - "
                f"{row['Anx'] + row['Grp']}",
                exc_info=False
            )
            return
        except Exception as e:
            logger.error(
                f"Error {e} while saving plan of action for "
                f"{row['CntryID']} - {row['PeriodID']} - "
                f"{row['Anx'] + row['Grp']}",
                exc_info=True
            )
            return

    def _import_plan_data(self, row, purge):
        decision = self.decisions.get(row["DecID"], None)
        create_data = {
            "party_id": self.parties[row["CntryID"]],
            "reporting_period_id": self.periods[row["PeriodID"]],
            "group_id": self.groups[row["Anx"] + row["Grp"]],
            "benchmark": row["Benchmark"],
            "annex_group_description": (
                row["AnxGrpDescription"] if row['AnxGrpDescription'] else '')
            ,
            "combined_id": False if row["CombinedID"] == 0 else True,
            "is_valid": row["isValid"],
            "decision_id": decision.id if decision else None,
        }

        if purge:
            PlanOfAction.objects.filter(
                party_id=create_data["party_id"],
                reporting_period_id=create_data["reporting_period_id"],
                group_id=create_data["group_id"],
            ).delete()
            logger.info(
                f"Deleting plan of action from entry with ID {row['ID']} for "
                f"{row['CntryID']} - {row['PeriodID']} - "
                f"{row['Anx'] + row['Grp']}"
            )
            return

        PlanOfAction.objects.create(**create_data)
        logger.info(
            f"Created plan of action from entry with ID {row['ID']} for "
            f"{row['CntryID']} - {row['PeriodID']} - {row['Anx'] + row['Grp']}"
        )
