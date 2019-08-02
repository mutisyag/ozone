import logging

from openpyxl import load_workbook

from django.core.management.base import BaseCommand
from django.db import transaction

from ozone.core.models import (
    FocalPoint,
    LicensingSystem,
    Party,
    User,
    Website,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import country profile data"

    def __init__(self):
        super().__init__(stdout=None, stderr=None, no_color=False)
        self.wb = None
        self.parties = {_party.name: _party for _party in Party.objects.all()}
        self.parties_abbr = {_party.abbr: _party for _party in Party.objects.all()}

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
            ('fp-LicSys', self.process_focal_points_data),
            ('LicSysEstablishment', self.process_licensing_system_data),
            ('Websites', self.process_website_data),
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
                "Error %s while saving focal point %s/%s", e, row['cntry'], row['name'],
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

    def process_licensing_system_data(self, row):
        try:
            return self._process_licensing_system_data(row)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(
                "Error %s while saving licensing system for %s",
                e,
                row['CntryID'],
                exc_info=True,
            )
            return 0

    @transaction.atomic()
    def _process_licensing_system_data(self, row):
        entry = self.get_licensing_system_data(row)

        LicensingSystem.objects.create(**entry)
        logger.info("Licensing system for %s imported", row['CntryID'])
        return True

    def get_licensing_system_data(self, row):
        try:
            party = self.parties_abbr[row['CntryID']]
        except KeyError as e:
            raise e

        has_ods, has_hfc = False, False
        if row["LicSys_Anx_A_to_E"]:
            has_ods = True
        if row["HFCLicSysEst"]:
            has_hfc = True

        return {
            "party_id": party.id,
            "has_ods": has_ods,
            "has_hfc": has_hfc,
            "date_reported_hfc": row["HFCLicSysRepDate"],
            "remarks": row["HFCLicSysSummary"] if row["HFCLicSysSummary"] else ""
        }

    def process_website_data(self, row):
        try:
            return self._process_website_data(row)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(
                "Error %s while saving website for %s and URL text: %s",
                e,
                row['Country'],
                row['URL_text'],
                exc_info=True,
            )
            return 0

    @transaction.atomic()
    def _process_website_data(self, row):
        entry = self.get_website_data(row)
        Website.objects.create(**entry)
        logger.info(
            "Website for %s and URL text: %s imported",
            row['Country'],
            row['URL_text']
        )
        return True

    def get_website_data(self, row):
        try:
            party = self.parties[row['Country']]
        except KeyError as e:
            import pdb; pdb.set_trace()
            raise e

        is_url_broken = False
        if row['Broken URL link']:
            is_url_broken = True
        return {
            "party_id": party.id,
            "url": row['URL'],
            "description": row['URL_text'] if row['URL_text'] else "",
            "is_url_broken": is_url_broken,
            "ordering_id": row['Order']
        }
