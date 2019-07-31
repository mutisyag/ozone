import logging

from openpyxl import load_workbook

from django.core.management.base import BaseCommand
from django.db import transaction

from ozone.core.models import (
    FocalPoint,
    Party,
    User,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import country profile data"

    def __init__(self):
        super().__init__(stdout=None, stderr=None, no_color=False)
        self.wb = None
        self.parties = {_party.name: _party for _party in Party.objects.all()}

    def add_arguments(self, parser):
        parser.add_argument('file', help="the xlsx input file")

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
            ('fp-LicSys', self.process_focal_points_data)
        ]

        for workbook_name, workbook_processor in workbook_processors:
            worksheet = self.wb[workbook_name]
            values = list(worksheet.values)
            headers = values[0]
            for row in values[1:]:
                row = dict(zip(headers, row))
                workbook_processor(row)

    def process_focal_points_data(self, row):
        try:
            return self._process_focal_points_data(row)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(
                "Error %s while saving transfer %s/%s", e, row['cntry'], row['name'],
                exc_info=True
            )
            return 0

    @transaction.atomic()
    def _process_focal_points_data(self, row):
        entry = self.get_focal_points_data(row)
        FocalPoint.objects.create(**entry)
        logger.info("Focal point %s/%s imported", row['cntry'], row['name'])
        return True

    def get_focal_points_data(self, row):
        try:
            party = self.parties[row['cntry']]
        except KeyError as e:
            if row["cntry"] == "Bolivia":
                party = self.parties["Bolivia (Plurinational State of)"]
            elif row["cntry"] == "Eswatini (the Kingdom of)":
                party = self.parties["Eswatini"]
            elif row["cntry"] == "Guinea-Bissau":
                party = self.parties["Guinea Bissau"]
            else:
                raise e
        addresses = [
            row["addr1"],
            row["addr2"],
            row["addr3"],
            row["addr4"],
            row["addr5"],
            row["addr6"]
        ]
        address = "\n".join(addr for addr in addresses if addr)

        is_licensing_system, is_national = False, False
        if row["fp-lic-sys"]:
            is_licensing_system = True
        if row["nfp"]:
            is_national = True

        return {
            "party_id": party.id,
            "name": row["name"] if row["name"] else "",
            "designation": row["designation"] if row["designation"] else "",
            "tel": row["tel"] if row["tel"] else "",
            "email": row["email"] if row["email"] else "",
            "fax": row["fax"] if row["fax"] else "",
            "address": address,
            "is_licensing_system": is_licensing_system,
            "is_national": is_national,
            "ordering_id": row["Order"]
        }
