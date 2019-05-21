from django.utils.translation import gettext_lazy as _
from reportlab.platypus import Paragraph, Table
from reportlab.lib import colors

from ozone.core.models import (
    ProdCons,
    Group,
    PartyHistory,
    Limit,
    LimitTypes,
    Submission,
    FormTypes,
)
from ozone.core.models.utils import round_half_up

from ..util import p_l
from ..util import h1_style, h2_style, h3_style, page_title_style, FONTSIZE_SMALL, TABLE_STYLES
from ..util import left_description_style
from ..util import col_widths


TABLE_CUSTOM_STYLES = (
    ('FONTSIZE', (0, 0), (-1, -1), FONTSIZE_SMALL),
    ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
    ('ALIGN', (1, 2), (-1, -1), 'RIGHT'),
    ('SPAN', (0, 0), (0, 1)), # annex/group
    ('SPAN', (1, 0), (4, 0)), # production
    ('SPAN', (5, 0), (9, 0)), # consumption
)

TABLE_TOTAL_STYLE = (
    ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold'),
)


def get_header(data):
    return Paragraph(
        data['tables'][0]['party']['name'].upper(),
        style=h1_style
    )


def get_subheader(data):
    description = _("""Production and Consumption for {period}
    - Comparison with Base Year""".format(
        period=data['period']))
    return Paragraph(
        description,
        style=h2_style
    )


def get_report_info(data):
    party = data['tables'][0]['party']
    info = _("""Date Reported: {date_reported}
                    {party_type} {party_region} - Population*: {population}""".format(
                        date_reported=party['date_reported'],
                        party_type=party['party_type'],
                        party_region=party['region'],
                        population=party['population']))
    return Paragraph(
        info,
        style=h3_style
    )


def get_description(groups):
    return tuple(
                p_l('{group} - {name} {description}. {description_alt}'.format(
                    group=k,
                    name=v['name'],
                    description=v['description'],
                    description_alt=v['description_alt']
                ), style=left_description_style)
                for k, v in groups.items()
        )


def get_ods_caption():
    description = _("""Production and Consumption of ODSs -
    Comparison with Base Year (ODP Tonnes)""")

    return Paragraph(
        description,
        style=page_title_style
    )


def get_ods_table(data):
    table_headers = data['headers']
    # get all except F Annex/Group
    table_data = tuple(v for k, v in data['tables'][0]['data'].items() if k!='F') 
    table_total = (data['total'],)

    return Table(
        table_headers + table_data + table_total,
        colWidths=col_widths([5.5, 1.5, 1.5, 1.2, 1.5, 1.5, 1.5, 1.2, 1.5, 2]),
        style=(TABLE_STYLES + TABLE_CUSTOM_STYLES + TABLE_TOTAL_STYLE),
        hAlign='LEFT'
    )


def get_fgas_table(data):
    table_headers = data['headers']
    table_data = (tuple(data['tables'][0]['data']['F']),)  # get F Annex/Group

    return Table(
        table_headers + table_data,
        colWidths=col_widths([5.5, 1.5, 1.5, 1.2, 1.5, 1.5, 1.5, 1.2, 1.5, 2]),
        style=(TABLE_STYLES + TABLE_CUSTOM_STYLES),
        hAlign='LEFT'
    )


def get_fgas_caption():
    description = _("""Production and Consumption of HFCs -
    Comparison with Base Year (CO2-equivalent tonnes)""")

    return Paragraph(
        description,
        style=page_title_style
    )


def get_prodcons_flowables(period, parties):
    data = get_prodcons_data(period, parties)

    flowables = list(
        (get_header(data),) +
        (get_subheader(data),) +
        (get_report_info(data),) +
        get_description(data['groups']) +
        (Paragraph("", style=page_title_style),) +
        (get_ods_caption(),) +
        (get_ods_table(data),) +
        (Paragraph("", style=page_title_style),)
    )

    if 'F' in data['tables'][0]['data'].keys():
        flowables.append(get_fgas_caption())
        flowables.append(get_fgas_table(data))

    return flowables


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

    data['headers'] = (
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
            period.name,
            _('Base'),
            _('Limit'),
            _('% Chng'),
            period.name,
            _('Base'),
            _('Limit'),
            _('% Chng'),
            _('Per Cap. Cons.')
        )
    )

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
        submission_qs = Submission.objects.filter(
            party=party,
            reporting_period=period,
            obligation___form_type=FormTypes.ART7.value
        )
        # There should only be one current submission.
        # TODO This list will be empty for submissions in data_entry.
        submission = [s for s in submission_qs if s.is_current is True][0]

        if submission.submitted_at:
            date_reported = submission.submitted_at.strftime("%d-%b-%Y")
        elif submission.info.date:
            date_reported = submission.info.date.strftime("%d-%b-%Y")
        else:
            date_reported = ''
        table_data['party'] = {
            'name': party.name,
            'population': "{:,}".format(history.population),
            'party_type': history.party_type.abbr,
            'date_reported': date_reported,
            'region': party.subregion.region.abbr
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
                per_capita_cons = round_half_up(
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
                    chng_prod = round_half_up(
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
                    chng_cons = round_half_up(
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

            table_data['data'][group.group_id] = (
                '{id}  - {descr}'.format(
                    id=group.group_id,
                    descr=group.description
                ),
                actual_prod,
                baseline_prod,
                chng_prod,
                limit_prod,
                actual_cons,
                baseline_cons,
                chng_cons,
                limit_cons,
                per_capita_cons
            )
        data['tables'].append(table_data)

    total['actual_prod'] = round_half_up(total['actual_prod'], 2)
    total['baseline_prod'] = round_half_up(total['baseline_prod'], 2)
    if total['actual_prod'] <= 0 or total['baseline_prod'] == 0:
        total['chng_prod'] = - 100
    else:
        total['chng_prod'] = round_half_up(
            -100 + total['actual_prod'] / total['baseline_prod'] * 100,
            2
        )
    total['actual_cons'] = round_half_up(total['actual_cons'], 2)
    total['baseline_cons'] = round_half_up(total['baseline_cons'], 2)
    if total['actual_cons'] <= 0 or total['baseline_cons'] == 0:
        total['chng_cons'] = - 100
    else:
        total['chng_cons'] = round_half_up(
            -100 + total['actual_cons'] / total['baseline_cons'] * 100,
            2
        )

    data['total'] = (
        'Sub-Total',
        total['actual_prod'],
        total['baseline_prod'],
        '',
        total['chng_prod'],
        total['actual_cons'],
        total['baseline_cons'],
        '',
        total['chng_cons'],
        ''
    )

    return data
