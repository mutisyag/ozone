from datetime import datetime

from ozone.core.models import (
    ProdCons,
    Group,
    PartyHistory,
    Limit,
    LimitTypes,
)


def export_prodcons(submission):
    data = get_prodcons_data(submission)
    #TODO


def get_prodcons_data(submission):
    data = {}
    all_groups = Group.objects.all()
    data['groups'] = {}
    for group in all_groups:
        data['groups'][group.group_id] = {
            'name': group.name_alt,
            'description': group.description,
            'description_alt': group.description_alt
        }

    period = submission.reporting_period
    data['period'] = period.name

    party = submission.party
    history = PartyHistory.objects.get(
        party=party,
        reporting_period=period
    )
    if submission.submitted_at:
        date_reported = submission.submitted_at
    else:
        date_reported = submission.info.date
    data['party'] = {
        'name': party.name,
        'population': history.population,
        'party_type': history.party_type.abbr,
        'date_reported': date_reported.strftime("%d-%b-%Y")
    }

    data['headers'] = {
        'PRODUCTION': ['2016', 'Base', '% Chng'],
        'CONSUMPTION': ['2016', 'Base', '% Chng', 'Per Cap. Cons.']
    }

    data['data'] = {}
    agg = submission.get_aggregated_data()
    to_report_groups = Group.get_report_groups(party, period)
    total = {
        'actual_prod': 0,
        'baseline_prod': 0,
        'actual_cons': 0,
        'baseline_cons': 0,
    }
    for group in all_groups:
        if agg.get(group):
            prodcons = agg[group]
            actual_prod = prodcons.calculated_production
            if prodcons.baseline_prod:
                baseline_prod = prodcons.baseline_prod
                if actual_prod <= 0 or baseline_prod == 0:
                    chng_prod = -100
                else:
                    chng_prod = round(
                        -100 + actual_prod / baseline_prod*100,
                        ProdCons.get_decimals(period, group, party)
                    )
            else:
                baseline_prod = 'NR'
                chng_prod = -100
            actual_cons = prodcons.calculated_consumption
            if prodcons.baseline_cons:
                baseline_cons = prodcons.baseline_cons
                if actual_cons <= 0 or baseline_cons == 0:
                    chng_cons = -100
                else:
                    chng_cons = round(
                        -100 + actual_cons / baseline_cons*100,
                        ProdCons.get_decimals(period, group, party)
                    )
            else:
                baseline_cons = 'NR'
                chng_cons = -100
            per_capita_cons = round(
                actual_cons / history.population,
                4
            )
            total['actual_prod'] += actual_prod
            total['baseline_prod'] += baseline_prod if baseline_prod != 'NR' else 0
            total['actual_cons'] += actual_cons
            total['baseline_cons'] += baseline_cons if baseline_cons != 'NR' else 0
        else:
            if group in to_report_groups:
                actual_prod = chng_prod = 'NR'
                actual_cons = chng_cons = per_capita_cons = 'NR'
            else:
                actual_prod = chng_prod = '-'
                actual_cons = chng_cons = per_capita_cons = '-'
            baseline_prod = baseline_cons = 'NR'

        limit_prod = Limit.objects.filter(
            party=party,
            reporting_period=period,
            group=group,
            limit_type=LimitTypes.PRODUCTION.value
        ).first()
        if limit_prod:
            limit_prod = limit_prod.limit
        limit_cons = Limit.objects.filter(
            party=party,
            reporting_period=period,
            group=group,
            limit_type=LimitTypes.CONSUMPTION.value
        ).first()
        if limit_cons:
            limit_cons = limit_cons.limit
        data['data'][group.group_id] = {
            'description': group.description,
            'actual_prod': actual_prod,
            'baseline_prod': baseline_prod,
            'chng_prod': chng_prod,
            'limit_prod': limit_prod,
            'actual_cons': actual_cons,
            'baseline_cons': baseline_cons,
            'chng_cons': chng_cons,
            'limit_cons': limit_cons,
            'per_capita_cons': per_capita_cons
        }
    total['actual_prod'] = round(total['actual_prod'], 2)
    total['baseline_prod'] = round(total['baseline_prod'], 2)
    if total['actual_prod'] <= 0:
        total['chng_prod'] = - 100
    else:
        total['chng_prod'] = round(
            -100 + total['actual_prod'] / total['baseline_prod'] * 100,
            2
        )
    total['actual_cons'] = round(total['actual_cons'], 2)
    total['baseline_cons'] = round(total['baseline_cons'], 2)
    if total['actual_cons'] <= 0:
        total['chng_cons'] = - 100
    else:
        total['chng_cons'] = round(
            -100 + total['actual_cons'] / total['baseline_cons'] * 100,
            2
        )
    data['data']['sub_total'] = total

    return data
