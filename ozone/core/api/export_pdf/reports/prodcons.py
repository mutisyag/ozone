from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from reportlab.platypus import Paragraph, Table
from reportlab.platypus import PageBreak

from ozone.core.models import (
    ProdCons,
    Group,
    PartyHistory,
    Baseline,
    Limit,
    LimitTypes,
    Submission,
    ObligationTypes,
)
from ozone.core.models.utils import round_decimal_half_up

from ..util import (
    h1_style, h2_style, sm_no_spacing_style,
    smb_l, sm_l, b_l,
    format_decimal,
    DOUBLE_HEADER_TABLE_STYLES,
    col_widths,
    get_date_of_reporting_str,
)


__all__ = [
    'get_prodcons_flowables',
]

TABLE_CUSTOM_STYLES = (
    ('ALIGN', (1, 2), (-1, -1), 'RIGHT'),
    ('SPAN', (0, 0), (0, 1)),  # annex/group
    ('SPAN', (1, 0), (4, 0)),  # production
    ('SPAN', (5, 0), (9, 0)),  # consumption
)


def get_header(party_name):
    return (
        Paragraph(party_name.upper(), style=h1_style),
        Paragraph("Production and Consumption - Comparison with Base Year", style=h2_style),
    )


def get_party_history(party_data):
    info = _("""{party_name} - Date Reported: {date_reported}
                    {party_type} {party_region} - Population*: {population}""".format(
                        party_name=party_data['name'],
                        date_reported=party_data['date_reported'],
                        party_type=party_data['party_type'],
                        party_region=party_data['region'],
                        population=party_data['population']))
    paragraph = b_l(info)
    paragraph.keepWithNext = True
    return paragraph


def get_groups_description(groups):
    return tuple(
                Paragraph('{group} - {name} {description}. {description_alt}'.format(
                    group=k,
                    name=v['name'],
                    description=v['description'],
                    description_alt=v['description_alt']
                ), sm_no_spacing_style)
                for k, v in groups.items()
        )


def get_table_header(period):
    return [
        (
            _('Annex/Group'),
            "{label}**".format(label=_('PRODUCTION')),
            '',
            '',
            '',
            "{label}**".format(label=_('CONSUMPTION')),
            '',
            '',
            '',
            ''
        ),
        (
            '',
            period,
            _('Base'),
            _('% Chng'),
            _('Limit'),
            period,
            _('Base'),
            _('% Chng'),
            _('Limit'),
            _('Per Cap. Cons.')
        ),
    ]


def get_table(table_data):
    rows = list()
    styles = list(DOUBLE_HEADER_TABLE_STYLES + TABLE_CUSTOM_STYLES)
    period = table_data['period']
    rows += get_table_header(period)
    # heading for ODS

    ods_caption = _("Production and Consumption of ODSs for {period} (ODP tonnes)")
    rows.append((
        smb_l(ods_caption.format(period=period)),
    ))
    current_row = len(rows) - 1
    styles.extend([
        ('SPAN', (0, current_row), (-1, current_row)),
    ])

    def _format(row):
        return (
            format_decimal(value) if isinstance(value, Decimal) else value
            for value in row
        )

    rows += [_format(v) for k, v in table_data['data'].items() if k != 'F']

    if 'F' in table_data['data'].keys():
        hfc_caption = _("Production and Consumption of HFCs for {period} (CO2-equivalent tonnes)")
        rows.append((
            smb_l(hfc_caption.format(period=period)),
        ))
        current_row = len(rows) - 1
        styles.extend([
            ('SPAN', (0, current_row), (-1, current_row)),
        ])
        rows.append(_format(table_data['data']['F']))

    return Table(
        rows,
        colWidths=col_widths([5.5, 1.5, 1.5, 1.2, 1.5, 1.5, 1.5, 1.2, 1.5, 2]),
        style=styles,
        hAlign='LEFT'
    )


def get_footer():
    return sm_l(_(
        """* Population in thousands <br/>
        ** Consumption and Production numbers are rounded to a uniform number of decimal places. <br/><br/>
        - = Data Not Reported and Party has no Obligation to have Reported that data at this time. <br/>
        N.R. = Data Not Reported but Party is required to have reported | 
        AFR = Africa | 
        ASIA = Asia | 
        EEUR = Eastern Europe | 
        LAC = Latin America & the Caribbean | 
        WEUR = Western Europe & others
        A5 = Article 5 Party | 
        NA5 = Non-Article 5 Party"""
    ))


def get_prodcons_flowables(submission, periods, parties):
    data = get_prodcons_data(submission, periods, parties)

    flowables = []
    for party_name, party_data in data['parties'].items():
        flowables += list(
            get_header(party_name) +
            get_groups_description(data['groups']) +
            (Paragraph("", style=h1_style),)
        )
        for table_data in party_data:
            flowables.append(get_party_history(table_data['party']))
            flowables.append(get_table(table_data))
            flowables.append(Paragraph('', style=h1_style))
        flowables += [get_footer(), PageBreak()]
    return flowables


def _get_table_data(party, period, prodcons_qs, submission, date_reported, all_groups):
    table_data = {}
    try:
        history = PartyHistory.objects.get(
            party=party,
            reporting_period=period
        )
        population = history.population
        party_type = history.party_type.abbr
        is_eu_member = history.is_eu_member
        is_article5 = history.is_article5
    except PartyHistory.DoesNotExist:
        return None

    table_data['period'] = period.name

    table_data['party'] = {
        'name': party.name,
        'population': '{:,}'.format(population) if population else '',
        'party_type': party_type,
        'date_reported': date_reported,
        'region': party.subregion.region.abbr
    }

    table_data['data'] = {}
    to_report_groups = Group.get_report_groups(party, period)
    controlled_groups = Group.get_controlled_groups(party, period)

    for group in all_groups:
        if submission is None:
            try:
                main_prodcons = prodcons_qs.get(group=group)
            except ProdCons.DoesNotExist:
                main_prodcons = None
        else:
            # In this case, prodcons_qs is actually a dict
            main_prodcons = prodcons_qs.get(group, None)

        if main_prodcons:
            # Get some pre-calculated values
            limit_prod = main_prodcons.limit_prod
            limit_cons = main_prodcons.limit_cons
            baseline_prod = main_prodcons.baseline_prod
            baseline_cons = main_prodcons.baseline_cons
        else:
            limit_prod = get_limit(
                party,
                period,
                group,
                LimitTypes.PRODUCTION.value,
            )
            limit_cons = get_limit(
                party,
                period,
                group,
                LimitTypes.CONSUMPTION.value,
            )
            baseline_prod = Baseline.objects.filter(
                party=party,
                group=group,
                baseline_type__name='A5Prod' if is_article5 else 'NA5Prod',
            ).first()
            baseline_prod = baseline_prod.baseline if baseline_prod else None
            baseline_cons = Baseline.objects.filter(
                party=party,
                group=group,
                baseline_type__name='A5Cons' if is_article5 else 'NA5Cons',
            ).first()
            baseline_cons = baseline_cons.baseline if baseline_cons else None

        if party.abbr == 'EU':
            main_prod = None
        else:
            main_prod = get_formatted_value(
                main_prodcons,
                'calculated_production',
                group,
                to_report_groups
            )
        if is_eu_member:
            main_cons = None
        else:
            main_cons = get_formatted_value(
                main_prodcons,
                'calculated_consumption',
                group,
                to_report_groups
            )
        per_capita_cons = get_per_capita_cons(main_cons, population)

        # % reduction vs base year
        chng_prod = get_chng(
            main_prod, baseline_prod
        ) if party.abbr != 'EU' else None

        chng_cons = get_chng(
            main_cons, baseline_cons
        ) if not is_eu_member else None

        baseline_prod = get_formatted_baseline(
            baseline_prod, main_prod, group, controlled_groups
        ) if party.abbr != 'EU' else None

        baseline_cons = get_formatted_baseline(
            baseline_cons, main_cons, group, controlled_groups
        ) if not is_eu_member else None

        limit_prod = get_formatted_limit(
            limit_prod
        ) if party.abbr != 'EU' else None

        limit_cons = get_formatted_limit(
            limit_cons
        ) if not is_eu_member else None

        if check_skip_group(
            [main_prod, baseline_prod, main_cons, baseline_cons]
        ):
            continue

        table_data['data'][group.group_id] = (
            '{id}  - {descr}'.format(
                id=group.group_id,
                descr=group.description
            ),

            main_prod,
            baseline_prod,
            chng_prod,
            limit_prod,

            main_cons,
            baseline_cons,
            chng_cons,
            limit_cons,

            per_capita_cons
            if not is_eu_member else None,
        )
    return table_data


def _get_date_reported(submission, prodcons_qs):
    if submission:
        return get_date_of_reporting_str(submission)
    # Get the date reported from the Article 7 submission related to ProdCons
    submission_id = None
    for subs in prodcons_qs.values_list('submissions', flat=True):
        id_list = subs.get(ObligationTypes.ART7.value, [])
        if id_list:
            submission_id = id_list[0]
    sub = Submission.objects.filter(id=submission_id).first()
    if sub:
        # There should only be one current submission.
        return get_date_of_reporting_str(sub)
    else:
        return "-"


def get_prodcons_data(submission, periods, parties):
    data = {}
    all_groups = Group.objects.all()
    data['groups'] = {}
    for group in all_groups:
        data['groups'][group.group_id] = {
            'name': group.name_alt,
            'description': group.description,
            'description_alt': group.description_alt
        }

    parties = [submission.party] if submission else parties
    periods = [submission.reporting_period] if submission else periods

    data['parties'] = {}
    for party in parties:
        data['parties'][party.name] = []
        for period in periods:
            if submission is None:
                prodcons_qs = ProdCons.objects.filter(
                    party=party,
                    reporting_period=period
                )
            else:
                # We need to get the actual data from *this* submission
                prodcons_qs = submission.get_aggregated_data()
            date_reported = _get_date_reported(submission, prodcons_qs)
            table_data = _get_table_data(
                party, period, prodcons_qs, submission, date_reported, all_groups
            )
            # Can be None for inactive parties / no history (e.g. Yugoslavia)
            if table_data:
                data['parties'][party.name].append(table_data)

    return data


def get_formatted_value(prodcons, field, group, to_report_groups):
    if prodcons and getattr(prodcons, field) is not None:
        actual_value = getattr(prodcons, field)
    else:
        if group in to_report_groups:
            actual_value = 'N.R.'
        else:
            actual_value = '-'
    return actual_value


def get_limit(party, period, group, limit_type):
    limit = Limit.objects.filter(
        party=party,
        reporting_period=period,
        group=group,
        limit_type=limit_type,
    ).first()
    return limit.limit if limit else None


def get_formatted_limit(limit):
    return limit if limit is not None else '-'


def get_formatted_baseline(baseline, actual, group, controlled_groups):
    # actual is get_formatted_value(production/consumption)
    if baseline is None:
        if group not in controlled_groups or group.group_id in ['CII', 'CIII']:
            return '-'
        return 'N.R.'
    else:
        return baseline if actual != '-' else '-'


def get_per_capita_cons(cons, population):
    if cons is None or isinstance(cons, str) or not population:
        return '-'
    else:
        return round_decimal_half_up(cons / population, 4)


def get_chng(actual_value, baseline):
    if isinstance(actual_value, str):
        return '-'
    elif actual_value <= 0:
        # even when baseline was not reported
        return -100
    elif baseline is None:
        return '-'
    elif actual_value > 0 and baseline != 0:
        return round_decimal_half_up(
            actual_value / baseline * 100 - 100,
            2
        )
    else:
        return -100


def check_skip_group(values):
    return all(
        val is None or val == '-' or val == ""
        for val in values
    )
