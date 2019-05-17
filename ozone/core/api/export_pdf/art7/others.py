from ozone.core.models import (
    ProdCons,
    Group,
    PartyHistory,
    Limit,
    LimitTypes,
    Submission,
    Obligation,
)


def export_prodcons(period, parties):
    data = get_prodcons_data(period, parties)
    #TODO


def get_prodcons_data(period, parties):
    data = {}
    all_groups = Group.objects.all()
    data['groups'] = {}
    for group in all_groups:
        data['groups'][group.group_id] = {
            'name': group.name_alt,
            'description': group.description,
            'description_alt': group.description_alt
        }

    data['headers'] = {
        'PRODUCTION': ['2016', 'Base', '% Chng'],
        'CONSUMPTION': ['2016', 'Base', '% Chng', 'Per Cap. Cons.']
    }

    data['period'] = period.name

    total = {
        'actual_prod': 0,
        'baseline_prod': 0,
        'actual_cons': 0,
        'baseline_cons': 0,
    }

    data['tables'] = []
    for party in parties:
        table_data = {}
        history = PartyHistory.objects.get(
            party=party,
            reporting_period=period
        )
        submission = Submission.objects.filter(
            party=party,
            reporting_period=period,
            obligation=Obligation.objects.get(name="Article 7 - Data Reporting")
        ).first()
        if submission.submitted_at:
            date_reported = submission.submitted_at.strftime("%d-%b-%Y")
        elif submission.info.date:
            date_reported = submission.info.date.strftime("%d-%b-%Y")
        else:
            date_reported = ''
        table_data['party'] = {
            'name': party.name,
            'population': history.population,
            'party_type': history.party_type.abbr,
            'date_reported': date_reported
        }

        table_data['data'] = {}
        to_report_groups = Group.get_report_groups(party, period)
        for group in all_groups:
            try:
                prodcons = ProdCons.objects.get(
                    party=party,
                    reporting_period=period,
                    group=group
                )
            except ProdCons.DoesNotExist:
                prodcons = None
            if prodcons and prodcons.calculated_production:
                actual_prod = prodcons.calculated_production
                total['actual_prod'] += actual_prod
            else:
                if group in to_report_groups:
                    actual_prod = 'NR'
                else:
                    actual_prod = '-'

            per_capita_cons = 0
            if prodcons and prodcons.calculated_consumption:
                actual_cons = prodcons.calculated_consumption
                total['actual_cons'] += actual_cons
                per_capita_cons = round(
                    actual_cons / history.population,
                    4
                )
            else:
                if group in to_report_groups:
                    actual_cons = 'NR'
                else:
                    actual_cons = '-'

            chng_prod = -100
            if prodcons and prodcons.baseline_prod:
                baseline_prod = prodcons.baseline_prod
                if not isinstance(actual_prod, str) and actual_prod > 0 and baseline_prod != 0:
                    chng_prod = round(
                        -100 + actual_prod / baseline_prod*100,
                        ProdCons.get_decimals(period, group, party)
                    )
                total['baseline_prod'] += baseline_prod
            else:
                baseline_prod = 'NR'

            chng_cons = -100
            if prodcons and prodcons.baseline_cons:
                baseline_cons = prodcons.baseline_cons
                if not isinstance(actual_cons, str) and actual_cons > 0 and baseline_cons != 0:
                    chng_cons = round(
                        -100 + actual_cons / baseline_cons*100,
                        ProdCons.get_decimals(period, group, party)
                    )
                total['baseline_cons'] += baseline_cons
            else:
                baseline_cons = 'NR'

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

            table_data['data'][group.group_id] = {
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
        data['tables'].append(table_data)

    total['actual_prod'] = round(total['actual_prod'], 2)
    total['baseline_prod'] = round(total['baseline_prod'], 2)
    if total['actual_prod'] <= 0 or total['baseline_prod'] == 0:
        total['chng_prod'] = - 100
    else:
        total['chng_prod'] = round(
            -100 + total['actual_prod'] / total['baseline_prod'] * 100,
            2
        )
    total['actual_cons'] = round(total['actual_cons'], 2)
    total['baseline_cons'] = round(total['baseline_cons'], 2)
    if total['actual_cons'] <= 0 or total['baseline_cons'] == 0:
        total['chng_cons'] = - 100
    else:
        total['chng_cons'] = round(
            -100 + total['actual_cons'] / total['baseline_cons'] * 100,
            2
        )
    data['total'] = total

    return data
