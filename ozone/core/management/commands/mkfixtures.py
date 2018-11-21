import json
import os

from django.core.management.base import BaseCommand, CommandError
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from openpyxl import load_workbook

from ozone.core.models.utils import RatificationTypes


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
        'party': {
            'sheet': 'Cntry',
            'fixture': 'parties.json',
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
    }

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
                filename = os.path.join(self.OUTPUT_DIR, self.MODELS[model]['fixture'])
                with open(filename, 'r', encoding='utf-8') as f:
                    self.FIXTURES[model] = json.load(f)
            except FileNotFoundError:
                continue

        for model in options['models']:
            data = self.parse_model(wb, model)
            filename = os.path.join(self.OUTPUT_DIR, self.MODELS[model]['fixture'])
            with open(filename, 'w', encoding="utf-8") as outfile:
                json.dump(
                    data, outfile,
                    indent=2, ensure_ascii=False, sort_keys=True,
                    cls=DjangoJSONEncoder
                )
                print('Done with %s' % filename)

    def row2dict(self, sheet, row):
        header = [cell.value for cell in sheet[1]]
        values = {}
        for key, cell in zip(header, row):
            values[key] = cell.value
        return values

    def lookup_id(self, model, field, key, data=None):
        # This method used to be pretty until UNK SubRegion appeared several times
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
            raise CommandError('Import for model "%s" is not implemented' % model)
        sheet = workbook[self.MODELS[model]['sheet']]

        for idx in range(1, sheet.max_row):
            row = self.row2dict(sheet, sheet[idx+1])
            obj = {
                'pk': idx,
                'model': 'core.' + model,
                'fields': {},
            }
            getattr(self, model + "_map")(obj['fields'], row)
            data.append(obj)

        # if a post process method exists, invoke it
        if hasattr(self, model + "_postprocess"):
            for idx in range(1, sheet.max_row):
                # This could be cached
                row = self.row2dict(sheet, sheet[idx+1])
                # Some not very nice assumptions made here
                obj = data[idx-1]
                getattr(self, model + "_postprocess")(obj['fields'], row)
        return data

    def region_map(self, f, row):
        f['name'] = row['RegionName']
        f['abbr'] = row['RegionID']
        f['remark'] = row['Remark'] or ''
        # unused: RegionNameFr, RegionNameSp

    def subregion_map(self, f, row):
        f['name'] = row['SubRegionName']
        f['abbr'] = row['SubRegionID']
        f['region'] = self.lookup_id('region', 'abbr', row['RegionID'])
        f['remark'] = row['Remark'] or ''

    def party_map(self, f, row):
        f['abbr'] = row['CntryID']
        f['name'] = row['CntryName']
        # Skipped fields: CntryNameFr, CntryNameSp, PrgApprDate, CntryID_org,
        # CntryName20, MDG_CntryCode, ISO_Alpha3Code, www_country_id

        # RegionID is not necessary because it's implied from SubRegionID
        subregion = self.lookup_id('subregion', 'abbr', row['SubRegionID'])
        if isinstance(subregion, list):
            # UNK subregion is not unique, so lookup_id will return a list
            region = self.lookup_id('region', 'abbr', row['RegionID'])
            subregion = self.lookup_id('subregion', 'region', region, subregion)
        f['subregion'] = subregion

        f['signed_vienna_convention'] = row['SignVC'].date() if row['SignVC'] else None
        f['signed_montreal_protocol'] = row['SignMP'].date() if row['SignMP'] else None

        f['ratification_date_vienna_convention'] = row['RD_VC'].date() if row['RD_VC'] else None
        f['ratification_date_montreal_amendment'] = row['RD_MP'].date() if row['RD_MP'] else None
        f['ratification_date_london_amendment'] = row['RD_LA'].date() if row['RD_LA'] else None
        f['ratification_date_copenhagen_amendment'] = row['RD_CA'].date() if row['RD_CA'] else None
        f['ratification_date_beijing_amendment'] = row['RD_MA'].date() if row['RD_MA'] else None
        f['ratification_date_kigali_amendment'] = row['RD_KA'].date() if row['RD_KA'] else None

        ratif_types_map = {
            'Ac': RatificationTypes.ACCESSION.value,
            'Ap': RatificationTypes.APPROVAL.value,
            'At': RatificationTypes.ACCEPTANCE.value,
            'R': RatificationTypes.RATIFICATION.value,
            'Sc': RatificationTypes.SUCCESSION.value,
            # TODO: What about RatificationTypes.SIGNING ??
        }
        f['ratification_type_vienna_convention'] = ratif_types_map.get(row['RT_VC'], "")
        f['ratification_type_montreal_protocol'] = ratif_types_map.get(row['RT_MP'], "")
        f['ratification_type_london_amendment'] = ratif_types_map.get(row['RT_LA'], "")
        f['ratification_type_copenhagen_amendment'] = ratif_types_map.get(row['RT_CA'], "")
        f['ratification_type_beijing_amendment'] = ratif_types_map.get(row['RT_BA'], "")
        f['ratification_type_kigali_amendment'] = ratif_types_map.get(row['RT_KA'], "")

        f['remark'] = row['Remark'] or ""

    def party_postprocess(self, f, row):
        # set parent party by looking up in the same data
        f['parent_party'] = self.lookup_id('party', 'abbr', row['MainCntryID'])

    def substance_map(self, f, row):
        f['substance_id'] = row['SubstID']
        f['name'] = row['SubstName']
        # Skipped fields: SubstNameFr, SubstNameSp
        annex = row['Anx']
        if annex and annex != '-':
            f['annex'] = self.lookup_id('annex', 'annex_id', annex)
            f['group'] = self.lookup_id('group', 'group_id', annex+row['Grp'])
        # TODO: sort order
        # f['sort_order'] = row['AnxGrpSort']
        f['odp'] = row['SubstODP']
        f['gwp'] = row['SubstGWP']
        f['max_odp'] = row['MaxODP']
        f['min_odp'] = row['MinODP']
        f['description'] = row['SubstDescr']
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

        # TODO: Not mapped: r_code, mp_control, main_usage

    def blend_map(self, f, row):
        f['blend_id'] = row['Blend']
        f['composition'] = row['Composition']
        f['other_names'] = row['OtherNames'] or ""
        f['remark'] = row['Remark'] or ""
        # TODO: Not mapped: main_usage, odp, hcfc, gwp, hfc, mp_control, type

    def blendcomponent_map(self, f, row):
        f['blend_id'] = self.lookup_id('blend', 'blend_id', row['Blend'])
        # TODO: Component and CNumber
        # f['component_name'] = row['Component']
        f['percentage'] = row['Percentage']
        # f['cnumber'] = row['CNumber']
        f['substance'] = self.lookup_id('substance', 'substance_id', row['SubstID'])

    def reportingperiod_map(self, f, row):
        f['name'] = row['PeriodID']
        f['start_date'] = row['StartDate'].date()
        f['end_date'] = row['EndDate'].date()
        f['description'] = row['PeriodDescr']
        f['is_year'] = f['name'][0].isdigit()
