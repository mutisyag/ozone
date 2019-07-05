import logging

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from openpyxl import load_workbook

from ozone.core.models import (
    Party,
    ReportingPeriod,
    Group,
    DeviationType,
    DeviationSource,
)


User = get_user_model()


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import deviation types and sources from legacy data"

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
            ("DeviationTypes", self.import_types_data),
            ("DeviationSources", self.import_sources_data),
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

    def import_types_data(self, row, purge=False):
        try:
            return self._import_types_data(row, purge)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(
                f"Error {e} while saving deviation "
                f"type {row['DeviationTypeID']}",
                exc_info=True
            )
            return

    @transaction.atomic
    def _import_types_data(self, row, purge):
        create_data = {
            "deviation_type_id": row["DeviationTypeID"],
            "description": row["DeviationType"],
            "deviation_pc": row["DeviationPC"],
            "remark": row["Remark"] if row["Remark"] else "",
        }
        if purge:
            DeviationType.objects.filter(
                deviation_type_id=create_data["deviation_type_id"]
            ).delete()
            logger.info(f"Deleted deviation type {row['DeviationTypeID']}")
            return

        DeviationType.objects.create(**create_data)
        logger.info(f"Created deviation type {row['DeviationTypeID']}")

    def import_sources_data(self, row, purge=False):
        try:
            return self._import_sources_data(row, purge)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(
                f"Error {e} while saving deviation source for "
                f"{row['CntryID']} in {row['PeriodID']}",
                exc_info=True
            )
            return

    def _import_sources_data(self, row, purge):
        create_data = {
            "party_id": self.parties[row["CntryID"]],
            "reporting_period_id": self.periods[row["PeriodID"]],
            "group_id": self.groups[row["Anx"] + row["Grp"]],
            "deviation_type_id": DeviationType.objects.filter(
                deviation_type_id=row["DeviationTypeID"]
            ).first().id,
            "production": row["Production"],
            "consumption": row["Consumption"],
            "remark": row["Remark"] if row["Remark"] else "",
        }

        if purge:
            DeviationSource.objects.filter(
                party_id=create_data["party_id"],
                reporting_period_id=create_data["reporting_period_id"],
                group_id=create_data["group_id"],
                deviation_type_id=create_data["deviation_type_id"],
            ).delete()
            logger.info(
                f"Deleted deviation source for {row['CntryID']} - "
                f"{row['PeriodID']} - {row['Anx'] + row['Grp']}, of type "
                f"{row['DeviationTypeID']}"
            )
            return

        DeviationSource.objects.create(**create_data)
        logger.info(
            f"Created deviation source for {row['CntryID']} - "
            f"{row['PeriodID']} - {row['Anx'] + row['Grp']}, of type "
            f"{row['DeviationTypeID']}"
        )
