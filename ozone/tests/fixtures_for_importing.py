from datetime import datetime
from ozone.core import models
from . import factories


def get_required_fixtures(data, blend_list):
    party_set = set()
    period_set = set()
    substance_set = set()
    submission_format_set = set()

    for row in data.tables['Overall'].rows:
        party_set.add(row['CntryID'])
        period_set.add(row['PeriodID'])
        submission_format_set.add(row['SubmissionType'])

    for row in data.tables['ImportNew'].rows:
        party_set.add(row['OrgCntryID'])

    for row in data.tables['Export'].rows:
        party_set.add(row['DestCntryID'])

    for row in data.tables['NonPartyTradeNew'].rows:
        party_set.add(row['SrcDestCntryID'])

    for sheet in ['Import', 'ImportNew', 'Export', 'Produce', 'Destroy',
                  'NonPartyTrade', 'NonPartyTradeNew']:
        for row in data.tables[sheet].rows:
            substance_set.add(row['SubstID'])

    blend_set = set(b[0] for b in blend_list)
    substance_set -= blend_set
    party_set -= set(['UNK'])

    return {
        'party_list': sorted(party_set),
        'period_list': sorted(period_set),
        'substance_list': sorted(substance_set - blend_set),
        'blend_list': blend_list,
        'submission_format_list': sorted(submission_format_set),
    }


def create_fixtures(subregion, party_list, period_list,
                    substance_list, blend_list=[],
                    submission_format_list=[],):
    for abbr in party_list:
        factories.PartyFactory(
            abbr=abbr,
            name=f"{abbr} party",
            subregion=subregion,
        )

    for name in period_list:
        factories.ReportingPeriodFactory(
            name=name,
            start_date=datetime.strptime('2009-01-01', '%Y-%m-%d'),
            end_date=datetime.strptime('2009-12-31', '%Y-%m-%d'),
        )

    for substance_id in substance_list:
        factories.SubstanceFactory(
            substance_id=substance_id,
            name=f"Chemical {substance_id}",
        )

    for legacy_blend_id, components in blend_list:
        blend = factories.BlendFactory(
            blend_id=str(legacy_blend_id),
            legacy_blend_id=legacy_blend_id,
        )
        for substance_id, percentage in components:
            blend.components.create(
                substance=models.Substance.objects.get(
                    substance_id=substance_id),
                percentage=percentage,
            )

    for name in submission_format_list:
        factories.SubmissionFormatFactory(
            name=name,
        )
