from datetime import datetime

import logging

from openpyxl import load_workbook

from django.core.management.base import BaseCommand
from django.db import transaction

from ozone.core.models import (
    FocalPoint,
    IllegalTrade,
    LicensingSystem,
    MultilateralFund,
    Obligation,
    ObligationTypes,
    OtherCountryProfileData,
    ORMReport,
    Party,
    ReclamationFacility,
    ReportingPeriod,
    User,
    URLTypes,
    Website
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import country profile data"

    def __init__(self):
        super().__init__(stdout=None, stderr=None, no_color=False)
        self.wb = None
        self.parties = {_party.name: _party for _party in Party.objects.all()}
        self.parties_abbr = {
            _party.abbr if _party.abbr != 'EU' else 'ECE': _party
            for _party in Party.objects.all()
        }
        self.periods = {
            _period.name: _period
            for _period in ReportingPeriod.objects.all()
        }

    def add_arguments(self, parser):
        parser.add_argument('file', help="the xlsx input file")
        parser.add_argument("-S", "--sheet", help="Only process this single sheet.")

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
            ('cp_Article_9', self.process_article9),
            ('cp_Env_Sound_Mgmt_strategies', self.process_ods_strategies),
            ('cp_Avoid_HCFC_Equip', self.process_unwanted_imports),
            ('cp_Reclamation_Facilities2', self.process_reclamation_facilities),
            ('cp_Illegal_Trade2', self.process_illegal_trades),
            ('cp_ORM_Reports', self.process_orm_reports),
            ('MLF', self.process_multilateral_funds),
        ]

        sheet = options["sheet"]
        if sheet:
            workbook_processors = [x for x in workbook_processors if x[0] == sheet]

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

    def process_article9(self, row):
        try:
            return self._process_article9(row)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(
                "Error %s while saving article9 for %s/%s/%s",
                e,
                row['Party'],
                row['PeriodID'],
                row['Publications_Title'],
                exc_info=True,
            )
            return 0

    @transaction.atomic()
    def _process_article9(self, row):
        entries = self.get_article9_data(row)
        for entry in entries:
            OtherCountryProfileData.objects.create(**entry)
            logger.info(
                "Article9 for %s/%s/%s imported",
                row['Party'],
                row['PeriodID'],
                entry['url_type']
            )
        return True

    def get_article9_data(self, row):
        try:
            party = self.parties[row['Party']]
        except KeyError as e:
            if row['Party'] == 'Venezuela':
                party = self.parties['Venezuela (Bolivarian Republic of)']
            elif row['Party'] == 'European Community':
                party = self.parties['European Union']
                row['Additonal Text for URL'] = "European Community"
            else:
                raise e
        try:
            period = self.periods[str(row['PeriodID'])]
        except KeyError as e:
            raise e

        urls = []
        if row['Submission URL']:
            urls.append(
                (
                    row['Submission URL'],
                    period.name,
                    URLTypes.SUBMISSION.value
                )
            )
        if row['Publications_URL']:
            urls.append(
                (
                    row['Publications_URL'],
                    row['Publications_Title'],
                    URLTypes.PUBLICATION.value
                )
            )
        if not row['Submission URL'] and not row['Publications_URL']:
            urls.append(
                ("", "", None)
            )

        entries = []
        for url, description, url_type in urls:
            entries.append({
                "party_id": party.id,
                "reporting_period_id": period.id,
                "obligation_id": Obligation.objects.filter(
                    _obligation_type=ObligationTypes.ART9.value
                ).first().id,
                "description": description,
                "url": url,
                "url_type": url_type,
                "remarks_secretariat": row["Additonal Text for URL"] if row["Additonal Text for URL"] else ""
            })
        return entries

    def process_ods_strategies(self, row):
        try:
            return self._process_ods_strategies(row)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(
                "Error %s while saving ODS strategies for %s",
                e,
                row['Party'],
                exc_info=True,
            )
            return 0

    @transaction.atomic()
    def _process_ods_strategies(self, row):
        entry = self.get_ods_strategies_data(row)
        OtherCountryProfileData.objects.create(**entry)
        logger.info(
            "ODS strategy for %s imported",
            row['Party'],
        )
        return True

    def get_ods_strategies_data(self, row):
        try:
            party = self.parties[row['Party']]
        except KeyError as e:
            raise e

        try:
            period = self.periods[str(row['PeriodID'])]
        except KeyError as e:
            raise e

        return {
            "party_id": party.id,
            "reporting_period_id": period.id,
            "obligation_id": Obligation.objects.filter(
                _obligation_type=ObligationTypes.ODSSTRATEGIES.value
            ).first().id,
            "url": row["URL"] if row["URL"] else "",
            "url_type": URLTypes.SUBMISSION.value
        }

    def process_unwanted_imports(self, row):
        try:
            return self._process_unwanted_imports(row)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(
                "Error %s while saving unwanted imports for %s",
                e,
                row['Party'],
                exc_info=True,
            )
            return 0

    @transaction.atomic()
    def _process_unwanted_imports(self, row):
        entry = self.get_unwanted_import_data(row)
        OtherCountryProfileData.objects.create(**entry)
        logger.info(
            "Unwanted import for %s imported",
            row['Party'],
        )
        return True

    def get_unwanted_import_data(self, row):
        try:
            party = self.parties[row['Party']]
        except KeyError as e:
            raise e

        try:
            period = self.periods[str(row['Document_Date'].year)]
        except KeyError as e:
            raise e

        return {
            "party_id": party.id,
            "reporting_period_id": period.id,
            "obligation_id": Obligation.objects.filter(
                _obligation_type=ObligationTypes.UNWANTEDIMPORTS.value
            ).first().id,
            "url": row["URL"] if row["URL"] else "",
            "url_type": URLTypes.SUBMISSION.value
        }

    def process_reclamation_facilities(self, row):
        try:
            return self._process_reclamation_facilities(row)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(
                "Error %s while saving reclamation facility for %s/%s",
                e,
                row['Party'],
                row['Facility_Name'],
                exc_info=True,
            )
            return 0

    @transaction.atomic()
    def _process_reclamation_facilities(self, row):
        entry = self.get_reclamation_facilities_data(row)
        ReclamationFacility.objects.create(**entry)
        logger.info(
            "Reclamation facility %s/%s imported",
            row['Party'],
            row['Facility_Name'],
        )
        return True

    def get_reclamation_facilities_data(self, row):
        try:
            party = self.parties[row['Party']]
        except KeyError as e:
            raise e

        return {
            "party_id": party.id,
            "date_reported": row['Report_Date'] if row['Report_Date'] else "",
            "name": row['Facility_Name'] if row['Facility_Name'] else "",
            "address": row['Address'] if row['Address'] else "",
            "reclaimed_substances": row['Reclaimed_Substances'] if row['Reclaimed_Substances'] else "",
            "capacity": row['Capacity'] if row['Capacity'] else "",
            "remarks": row['Remarks'] if row['Remarks'] else "",
        }

    def process_illegal_trades(self, row):
        try:
            return self._process_illegal_trades(row)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(
                "Error %s while saving illegal trade for %s/%s",
                e,
                row['Party'],
                row['Substances_Traded'],
                exc_info=True,
            )
            return 0

    @transaction.atomic()
    def _process_illegal_trades(self, row):
        entry = self.get_illegal_trade_data(row)
        if entry:
            IllegalTrade.objects.create(**entry)
            logger.info(
                "Illegal trade for %s/%s imported",
                row['Party'],
                row['Substances_Traded'],
            )
            return True

    def get_illegal_trade_data(self, row):
        try:
            party = self.parties[row['Party']]
        except KeyError as e:
            if row['Party'] == "Federated States of Micronesia":
                party = self.parties['Micronesia (Federated States of)']
            elif row['Party'] == "PARAGUAY":
                party = self.parties['Paraguay']
            else:
                # Sheet contains empty rows.
                if not row['Party']:
                    return
                raise e
        seisure_date = row['Seizure_Date_Year'] if row['Seizure_Date_Year'] else ""
        if type(seisure_date) == datetime:
            seisure_date = seisure_date.strftime('%d-%m-%Y')
        return {
            "party_id": party.id,
            "submission_id": row['Submission ID'],
            "seizure_date_year": seisure_date,
            "substances_traded": row['Substances_Traded'] if row['Substances_Traded'] else "",
            "volume": row['Volume'] if row['Volume'] else "",
            "importing_exporting_country": row['Importing_Exporting_Country'] if row['Importing_Exporting_Country'] else "",
            "illegal_trade_details": row['Illegal_Trade_Details'] if row['Illegal_Trade_Details'] else "",
            "action_taken": row['Action_Taken'] if row['Action_Taken'] else "",
            "remarks": row['Remark'] if row['Remark'] else "",
            "ordering_id": row['Sec_Order']
        }

    def process_orm_reports(self, row):
        try:
            return self._process_orm_reports(row)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(
                "Error %s while saving ORM Report for %s/%s/%s",
                e,
                row['CntryID'],
                row['Meeting'],
                row['Year'],
                exc_info=True,
            )
            return 0

    @transaction.atomic()
    def _process_orm_reports(self, row):
        entry = self.get_orm_report_data(row)
        ORMReport.objects.create(**entry)
        logger.info(
            "ORM Report for %s/%s/%s imported",
            row['CntryID'],
            row['Meeting'],
            row['Year'],
        )
        return True

    def get_orm_report_data(self, row):
        try:
            party = self.parties_abbr[row['CntryID']]
        except KeyError as e:
            raise e

        try:
            period = self.periods[str(row['Year'])]
        except KeyError as e:
            raise e

        description = row['Extra Text for URL']
        if not description or description == "\\N":
            description = ""
        return {
            "party_id": party.id,
            "meeting": row['Meeting'] if row['Meeting'] else "",
            "reporting_period_id": period.id,
            "description": description ,
            "url": row['URL'] if row['URL'] else ""
        }

    def process_multilateral_funds(self, row):
        try:
            return self._process_multilateral_funds(row)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(
                "Error %s while saving multilateral fund for %s",
                e,
                row['Country'],
                exc_info=True,
            )
            return 0

    @transaction.atomic()
    def _process_multilateral_funds(self, row):
        entry = self.get_multilateral_fund_data(row)
        if entry:
            MultilateralFund.objects.create(**entry)
            logger.info(
                "Multilateral fund for %s imported",
                row['Country'],
            )
        else:
            logger.info(
                "Multilateral fund for %s skipped",
                row['Country'],
            )
        return True

    def get_multilateral_fund_data(self, row):
        try:
            party = self.parties[row['Country']]
        except KeyError as e:
            if row['Country'] == 'Bolivia':
                party = self.parties['Bolivia (Plurinational State of)']
            elif row['Country'] == 'Cape Verde':
                party = self.parties['Cabo Verde']
            elif row['Country'] == 'Congo, DR':
                party = self.parties['Democratic Republic of the Congo']
            elif row['Country'] == "Cote D'Ivoire":
                party = self.parties["Côte d'Ivoire"]
            elif row['Country'] == 'Guinea-Bissau':
                party = self.parties["Guinea Bissau"]
            elif row['Country'] == 'Iran':
                party = self.parties['Iran (Islamic Republic of)']
            elif row['Country'] == 'Korea, DPR':
                party = self.parties["Democratic People's Republic of Korea"]
            elif row['Country'] == 'Lao, PDR':
                party = self.parties["Lao People's Democratic Republic"]
            elif row['Country'] == 'Micronesia':
                party = self.parties['Micronesia (Federated States of)']
            elif row['Country'] == 'Moldova, Rep':
                party = self.parties['Republic of Moldova']
            elif row['Country'] == 'Syria':
                party = self.parties['Syrian Arab Republic']
            elif row['Country'] == 'Tanzania':
                party = self.parties['United Republic of Tanzania']
            elif row['Country'] == 'Timor Leste':
                party = self.parties['Timor-Leste']
            elif row['Country'] == 'Venezuela':
                party = self.parties['Venezuela (Bolivarian Republic of)']
            elif row['Country'] == 'Vietnam':
                party = self.parties['Viet Nam']
            elif row['Country'] in [
                'Global',
                'Region: AFR',
                'Region: ASP',
                'Region: EUR',
                'Region: LAC',
            ]:
                return None
            else:
                raise e

        return {
            "party_id": party.id,
            "funds_approved": row['Funds approved '],
            "funds_disbursed": row[' Funds disbursed '],
            "date_approved": datetime.strptime("31-May-2019", "%d-%b-%Y"),
            "date_disbursed": datetime.strptime("31-Dec-2017", "%d-%b-%Y"),
        }
