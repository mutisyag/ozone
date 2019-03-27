import json
import os
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from openpyxl import load_workbook

from ozone.core.models.utils import RatificationTypes
from ozone.core.models.substance import Blend


class Command(BaseCommand):
    help = "Create fixtures from an Excel file"

    MODELS = {
        'annex': {
            'fixture': 'annexes.json',
        },
        'group': {
            'fixture': 'groups.json',
        },
        'language': {
            'fixture': 'languages.json',
        },
        'meeting': {
            'fixture': 'meetings.json',
        },
        'partytype': {
            'fixture': 'partytypes.json'
        },
        'party': {
            'sheet': 'Cntry',
            'fixture': 'parties.json',
        },
        'partyhistory': {
            'fixture': 'partieshistory.json',
            'sheet': 'CntryYr',
        },
        'partyratification': {
            'fixture': 'partiesratification.json',
            'sheet': 'Cntry',
        },
        'region': {
            'sheet': 'Regions',
            'fixture': 'regions.json',
        },
        'subregion': {
            'sheet': 'SubRegion',
            'fixture': 'subregions.json',
        },
        'treaty': {
            'fixture': 'treaties.json',
        },
        'substance': {
            'fixture': 'substances.json',
            'sheet': 'Subst',
        },
        'blend': {
            'fixture': 'blends.json',
            'sheet': 'Blends',
        },
        'blendcomponent': {
            'fixture': 'blend_components.json',
            'sheet': 'BlendComposition',
        },
        'reportingperiod': {
            'fixture': 'reportingperiods.json',
            'sheet': 'Period',
        },
        'substance_edw': {
            'model': 'substance',
            'min_id': 120,
            'fixture': 'substances_edw.json',
            'sheet': 'SubstEDW',
        },
    }
    EXCLUDED = (
        'UNK',
        'CZS',
    )

    OUTPUT_DIR = settings.FIXTURE_DIRS[0]
    FIXTURES = {}

    def add_arguments(self, parser):
        parser.add_argument('file',
                            help="the xlsx input file")
        parser.add_argument('models', nargs='+',
                            help="a list of meta-models to generate, e.g. party, substance")

    def handle(self, *args, **options):
        wb = load_workbook(filename=options['file'])

        # preload existing fixtures for dependent models
        for model in self.MODELS.keys():
            try:
                filename = os.path.join(
                    self.OUTPUT_DIR, self.MODELS[model]['fixture'])
                with open(filename, 'r', encoding='utf-8') as f:
                    self.FIXTURES[model] = json.load(f)
            except FileNotFoundError:
                continue

        for model in options['models']:
            data = self.parse_model(wb, model)
            filename = os.path.join(
                self.OUTPUT_DIR, self.MODELS[model]['fixture'])
            with open(filename, 'w', encoding="utf-8") as outfile:
                json.dump(
                    data, outfile,
                    indent=2, ensure_ascii=False, sort_keys=True,
                    cls=DjangoJSONEncoder
                )
                print('Done with %s' % filename)

    def row2dict(self, sheet, row, index):
        header = [cell.value for cell in sheet[1]]
        values = {}
        for key, cell in zip(header, row):
            values[key] = cell.value
        values['_index'] = index
        return values

    def lookup_id(self, model, field, key, data=None):
        # This method used to be pretty until UNK SubRegion appeared several
        # times
        if not key:
            return None
        if not data:
            data = self.FIXTURES[model]
        objs = list(filter(lambda x: x['fields'][field] == key, data))
        if len(objs) == 0:
            raise CommandError('Cannot find "{}" having "{}" = "{}"'.format(
                model, field, key
            ))
        if len(objs) == 1:
            return objs[0]['pk']
        return objs

    def parse_model(self, workbook, model):
        # reinitialize current model in FIXTURES
        data = self.FIXTURES[model] = []
        if not self.MODELS.get(model) or not self.MODELS[model].get('sheet'):
            raise CommandError(
                'Import for model "%s" is not implemented' % model)
        sheet = workbook[self.MODELS[model]['sheet']]

        for idx in range(1, sheet.max_row):
            row = self.row2dict(sheet, sheet[idx + 1], idx)
            model_class = 'core.' + (self.MODELS[model].get('model') or model)
            obj = {
                'pk': len(data) + 1 + (self.MODELS[model].get('min_id') or 0),
                'model': model_class,
                'fields': {},
            }
            fields = getattr(self, model + "_map")(obj['fields'], row)
            if isinstance(fields, dict):
                obj['fields'] = fields
                data.append(obj)
            elif isinstance(fields, list):
                # multiple objects returned
                for idx, f in enumerate(fields):
                    data.append({
                        'pk': obj['pk'] + idx,
                        'model': obj['model'],
                        'fields': f,
                    })
                pass
            else:
                # Probably None was returned, don't add to list
                continue

        if hasattr(self, model + "_additional_data"):
            data += getattr(self, model + "_additional_data")(len(data) + 1)

        # if a post process method exists, invoke it
        if hasattr(self, model + "_postprocess"):
            for obj in data:
                getattr(self, model + "_postprocess")(obj['fields'])
        # Hack alert: Remove rows having a pseudo-field called "_deleted"
        # return list(filter(lambda obj: obj['fields'].get('_deleted') is not
        # True, data))
        return data

    def region_map(self, f, row):
        f['name'] = row['RegionName']
        f['abbr'] = row['RegionID']
        f['remark'] = row['Remark'] or ''
        # unused: RegionNameFr, RegionNameSp
        return f

    def subregion_map(self, f, row):
        f['name'] = row['SubRegionName']
        f['abbr'] = row['SubRegionID']
        f['region'] = self.lookup_id('region', 'abbr', row['RegionID'])
        f['remark'] = row['Remark'] or ''
        return f

    def party_map(self, f, row):
        f['abbr'] = row['CntryID']
        if row['CntryID'][:2] == 'ZZ' or row['CntryID'].upper() in self.EXCLUDED:
            # Remove "All countries" and "Some countries"
            # f['_deleted'] = True
            return None
        f['name'] = row['CntryName']
        # Skipped fields: CntryNameFr, CntryNameSp, PrgApprDate, CntryID_org,
        # CntryName20, MDG_CntryCode, ISO_Alpha3Code, www_country_id

        # RegionID is not necessary because it's implied from SubRegionID
        subregion = self.lookup_id('subregion', 'abbr', row['SubRegionID'])
        if isinstance(subregion, list):
            # UNK subregion is not unique, so lookup_id will return a list
            region = self.lookup_id('region', 'abbr', row['RegionID'])
            subregion = self.lookup_id(
                'subregion', 'region', region, subregion)
        f['subregion'] = subregion

        f['remark'] = row['Remark'] or ""
        # This will be replaced in party_postprocess
        f['parent_party'] = row['MainCntryID']
        return f

    def party_postprocess(self, f):
        # set parent party by looking up in the same data
        if 'parent_party' in f:
            f['parent_party'] = self.lookup_id(
                'party', 'abbr', f['parent_party'])

    def partyhistory_map(self, f, row):
        if row['CntryID'] == 'HOLV' or row['CntryID'].upper() in self.EXCLUDED:
            # f['party'] = self.lookup_id('party', 'abbr', 'VA')
            # f['_deleted'] = True
            return None
        else:
            f['party'] = self.lookup_id('party', 'abbr', row['CntryID'])
        f['reporting_period'] = self.lookup_id(
            'reportingperiod', 'name', row['PeriodID'])
        f['population'] = row['Population'] if row['Population'] else 0
        art5_group2 = ["BH", "IN", "IR", "IQ",
                       "KW", "OM", "PK", "QA", "SA", "AE"]
        non_art5_group2 = ["BY", "KZ", "RU", "TJ", "UZ"]
        period_datetime = datetime.strptime(
            self.FIXTURES['reportingperiod'][
                f['reporting_period'] - 1]['fields']['end_date'], "%Y-%m-%d"
        )
        if period_datetime < datetime.strptime('2019-01-01', "%Y-%m-%d"):
            if row['Article5']:
                f['party_type'] = self.lookup_id(
                    'partytype', 'name', 'Article 5'
                )
                f['is_article5'] = True
            else:
                f['party_type'] = self.lookup_id(
                    'partytype', 'name', 'Non Article 5'
                )
                f['is_article5'] = False
        else:
            if row['Article5']:
                if row['CntryID'] in art5_group2:
                    f['party_type'] = self.lookup_id(
                        'partytype', 'name', 'Article 5 Group 2'
                    )
                else:
                    f['party_type'] = self.lookup_id(
                        'partytype', 'name', 'Article 5 Group 1'
                    )
                f['is_article5'] = True
            else:
                if row['CntryID'] in non_art5_group2:
                    f['party_type'] = self.lookup_id(
                        'partytype', 'name', 'Non Article 5 Group 2'
                    )
                else:
                    f['party_type'] = self.lookup_id(
                        'partytype', 'name', 'Non Article 5 Group 1'
                    )
                f['is_article5'] = False

        hat_parties = [
            "DZ", "BH", "BJ", "BF", "CF", "TD", "CI", "DJ", "EG", "ER", "GM",
            "GH", "GN", "GW", "IR", "IQ", "JO", "KW", "LY", "ML", "MR", "NE",
            "NG", "OM", "PK", "QA", "SA", "SN", "SD", "SY", "TG", "TN", "TM", "AE"
        ]
        if row['CntryID'] in hat_parties:
            f['is_high_ambient_temperature'] = True
        else:
            f['is_high_ambient_temperature'] = False
        f['is_eu_member'] = row['EurUnion']
        f['is_ceit'] = row['CEIT']
        f['remark'] = row['Remark'] if row['Remark'] else ""
        return f

    def partyratification_map(self, f, row):
        if row['CntryID'][:2] == 'ZZ' or row['CntryID'] != row['MainCntryID'] \
                or row['CntryID'].upper() in self.EXCLUDED:
            # Remove "All countries" and "Some countries"
            return None
        ratif_types_map = {
            'Ac': RatificationTypes.ACCESSION.value,
            'Ap': RatificationTypes.APPROVAL.value,
            'At': RatificationTypes.ACCEPTANCE.value,
            'R': RatificationTypes.RATIFICATION.value,
            'Sc': RatificationTypes.SUCCESSION.value,
            # TODO: What about RatificationTypes.SIGNING ??
        }
        objs = []
        party = self.lookup_id('party', 'abbr', row['CntryID'])
        treaties = ['VC', 'MP', 'LA', 'CA', 'MA', 'BA', 'KA']
        for treaty_id in treaties:
            if row['RD_' + treaty_id]:
                ratification_date = row['RD_' + treaty_id].date()
                ratification_date = row['RD_' + treaty_id].date()
                entry_into_force_date = row['EIF_' + treaty_id].date()
                objs.append({
                    'party': party,
                    'treaty': self.lookup_id('treaty', 'treaty_id', treaty_id),
                    'ratification_type': ratif_types_map.get(row['RT_' + treaty_id], ""),
                    'ratification_date': ratification_date,
                    'entry_into_force_date': entry_into_force_date,
                })
        return objs

    def substance_map(self, f, row):
        f['substance_id'] = row['SubstID']
        f['name'] = row['SubstName']
        # Skipped fields: SubstNameFr, SubstNameSp
        annex = row['Anx']
        if annex and annex != '-':
            group = annex + row['Grp']
            if f['name'] == 'HFC-23':
                group = 'FII'
            if group == 'FIII':
                return
            f['group'] = self.lookup_id('group', 'group_id', group)
        f['sort_order'] = row['AnxGrpSort'] or 9999
        f['odp'] = row['SubstODP']
        f['gwp'] = row['SubstGWP']
        f['max_odp'] = row['MaxODP'] or 0
        f['min_odp'] = row['MinODP'] or 0
        f['description'] = row['SubstDescr'] or row['SubstName']
        f['formula'] = row['SubstFormula'] or ""
        f['number_of_isomers'] = row['Number of Isomers']
        f['gwp2'] = row['GWP']
        f['gwp_error_plus_minus'] = row['GWP_Error_Plus_Minus']
        f['remark'] = row['Remark'] or ""
        f['carbons'] = row['Carbons'] or ""
        f['hydrogens'] = row['Hydrogens'] or ""
        f['fluorines'] = row['Fluorines'] or ""
        f['chlorines'] = row['Chlorines'] or ""
        f['bromines'] = row['Bromines'] or ""
        f['is_contained_in_polyols'] = f['name'] in ['CFC-11', 'HCFC-141B']

        # TODO: Not mapped: r_code, mp_control, main_usage
        return f

    def substance_edw_map(self, f, row):
        f['r_code'] = row['RCode']
        f['main_usage'] = row['MainUsage'] or ""
        return self.substance_map(f, row)

    def blend_map(self, f, row):
        f['blend_id'] = row['Blend']
        if f['blend_id'].startswith('R-4'):
            f['type'] = Blend.BlendTypes.ZEOTROPE.value
            f['sort_order'] = 1000 + row['_index']
        elif f['blend_id'].startswith('R-5'):
            f['type'] = Blend.BlendTypes.AZEOTROPE.value
            f['sort_order'] = 2000 + row['_index']
        elif f['blend_id'].startswith('MeBr'):
            f['type'] = Blend.BlendTypes.MeBr.value
            f['sort_order'] = 4000 + row['_index']
        else:
            f['type'] = Blend.BlendTypes.OTHER.value
            f['sort_order'] = 3000 + row['_index']

        f['composition'] = row['Composition']
        f['other_names'] = row['OtherNames'] or ""
        f['remark'] = row['Remark'] or ""
        # TODO: Not mapped: main_usage, odp, hcfc, gwp, hfc, mp_control, type
        return f

    def blendcomponent_map(self, f, row):
        f['blend_id'] = self.lookup_id('blend', 'blend_id', row['Blend'])
        f['component_name'] = row['Component'] or ""
        f['percentage'] = row['Percentage']
        f['cnumber'] = row['CNumber'] or ""
        substance = self.lookup_id('substance', 'substance_id', row['SubstID'])
        if not substance:
            substance = self.lookup_id(
                'substance_edw', 'name', row['Component'])
        f['substance'] = substance
        return f

    def reportingperiod_map(self, f, row):
        f['name'] = row['PeriodID']
        f['start_date'] = row['StartDate'].date()
        f['end_date'] = row['EndDate'].date()
        f['description'] = row['PeriodDescr']
        f['is_reporting_allowed'] = f['name'][0] == 'C' or (
            f['name'].isdigit() and int(f['name']) <= 2018
        )
        f['is_reporting_open'] = f['name'] in ('2017', '2018')
        return f

    def reportingperiod_additional_data(self, idx):
        objs = [
            {
                "fields": {
                    "description": "",
                    "end_date": datetime.strptime("1987-12-31", "%Y-%m-%d").date(),
                    "is_reporting_allowed": False,
                    "is_reporting_open": False,
                    "name": "1987",
                    "start_date": datetime.strptime("1987-01-01", "%Y-%m-%d").date()
                },
                "model": "core.reportingperiod",
                "pk": idx
            },
            {
                "fields": {
                    "description": "",
                    "end_date": datetime.strptime("1988-12-31", "%Y-%m-%d").date(),
                    "is_reporting_allowed": False,
                    "is_reporting_open": False,
                    "name": "1988",
                    "start_date": datetime.strptime("1988-01-01", "%Y-%m-%d").date()
                },
                "model": "core.reportingperiod",
                "pk": idx + 1
            }
        ]
        return objs
