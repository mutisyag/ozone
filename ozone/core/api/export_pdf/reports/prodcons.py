from django.utils.translation import gettext_lazy as _
from reportlab.platypus import Paragraph, Table
from reportlab.lib import colors
from reportlab.platypus import PageBreak

from ozone.core.models import (
    ProdCons,
    Group,
    PartyHistory,
    Limit,
    LimitTypes,
    Submission,
    FormTypes,
    ReportingPeriod,
)
from ozone.core.models.utils import round_half_up

from ..util import p_l
from ..util import h1_style, h2_style, h3_style, page_title_style, FONTSIZE_SMALL, TABLE_STYLES
from ..util import left_description_style
from ..util import col_widths
from ..util import (
    get_date_of_reporting_str,
    get_compared_period,
)


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


def get_header(table):
    return Paragraph(
        table['party']['name'].upper(),
        style=h1_style
    )


def get_subheader(data):
    description = _(
        "Production and Consumption for {period1} - "
        "Comparison with {period2} Year".format(
            period1=data['periods'][0],
            period2=data['periods'][1]
        )
    )
    return Paragraph(description, style=h2_style)


def get_report_info(table):
    party = table['party']
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


def get_ods_caption(compared_period):
    description = _(
        "Production and Consumption of ODSs - "
        "Comparison with {compared_period} Year (ODP Tonnes)".format(
            compared_period=compared_period
        )
    )

    return Paragraph(
        description,
        style=page_title_style
    )


def get_ods_table(headers, table):
    table_headers = headers
    # get all except F Annex/Group
    table_data = tuple(v for k, v in table['data'].items() if k!='F')

    return Table(
        table_headers + table_data,
        colWidths=col_widths([5.5, 1.5, 1.5, 1.2, 1.5, 1.5, 1.5, 1.2, 1.5, 2]),
        style=(TABLE_STYLES + TABLE_CUSTOM_STYLES),
        hAlign='LEFT'
    )


def get_fgas_table(headers, table):
    table_headers = headers
    table_data = (tuple(table['data']['F']),)  # get F Annex/Group

    return Table(
        table_headers + table_data,
        colWidths=col_widths([5.5, 1.5, 1.5, 1.2, 1.5, 1.5, 1.5, 1.2, 1.5, 2]),
        style=(TABLE_STYLES + TABLE_CUSTOM_STYLES),
        hAlign='LEFT'
    )


def get_fgas_caption(compared_period):
    description = _(
        "Production and Consumption of HFCs - "
        "Comparison with {compared_period} Year (CO2-equivalent tonnes)".format(
            compared_period=compared_period
        )
    )

    return Paragraph(
        description,
        style=page_title_style
    )


def get_prodcons_flowables(periods, parties):
    data = get_prodcons_data(periods, parties)

    pages = []
    for table in data['tables']:
        flowables = list(
            (get_header(table),) +
            (get_subheader(data),) +
            (get_report_info(table),) +
            get_description(data['groups']) +
            (Paragraph("", style=page_title_style),) +
            (get_ods_caption(periods[1].name),) +
            (get_ods_table(data['headers'], table),) +
            (Paragraph("", style=page_title_style),)
        )

        if 'F' in table['data'].keys():
            flowables.append(get_fgas_caption(periods[1].name))
            flowables.append(get_fgas_table(data['headers'], table))
        pages += flowables
        pages.append(PageBreak(),)
    return pages


def get_prodcons_data(periods, parties):
    data = {}
    all_groups = Group.objects.all()
    data['groups'] = {}
    for group in all_groups:
        data['groups'][group.group_id] = {
            'name': group.name_alt,
            'description': group.description,
            'description_alt': group.description_alt
        }

    periods = get_compared_period(periods)
    main_period = periods[0]
    compared_period = periods[1]

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
            main_period.name,
            compared_period.name,
            _('% Chng'),
            _('Limit'),
            main_period.name,
            compared_period.name,
            _('% Chng'),
            _('Limit'),
            _('Per Cap. Cons.')
        )
    )

    data['periods'] = [main_period.name, compared_period.name]

    data['tables'] = []
    for party in parties:
        table_data = {}
        history = PartyHistory.objects.get(
            party=party,
            reporting_period=main_period
        )
        submission_qs = Submission.objects.filter(
            party=party,
            reporting_period=main_period,
            obligation___form_type=FormTypes.ART7.value,
        )

        if submission_qs:
            # There should only be one current submission.
            submission = [s for s in submission_qs if s.is_current is True][0]
            date_reported = get_date_of_reporting_str(submission)
        else:
            date_reported = "-"

        table_data['party'] = {
            'name': party.name,
            'population': "{:,}".format(history.population),
            'party_type': history.party_type.abbr,
            'date_reported': date_reported,
            'region': party.subregion.region.abbr
        }

        table_data['data'] = {}
        to_report_groups_main_period = Group.get_report_groups(party, main_period)
        for group in all_groups:
            try:
                main_prodcons = ProdCons.objects.get(
                    party=party, reporting_period=main_period, group=group
                )
            except ProdCons.DoesNotExist:
                main_prodcons = None

            main_prod = get_actual_value(
                main_prodcons,
                'calculated_production',
                group,
                to_report_groups_main_period
            )
            limit_prod = get_limit(
                party,
                main_period,
                group,
                LimitTypes.PRODUCTION.value,
            )

            main_cons = get_actual_value(
                main_prodcons,
                'calculated_consumption',
                group,
                to_report_groups_main_period
            )
            limit_cons = get_limit(
                party,
                main_period,
                group,
                LimitTypes.CONSUMPTION.value,
            )
            per_capita_cons = get_per_capita_cons(main_cons, history.population)

            if isinstance(compared_period, ReportingPeriod):
                to_report_groups_compared_period = Group.get_report_groups(
                    party,
                    compared_period
                )
                try:
                    compared_prodcons = ProdCons.objects.get(
                        party=party, reporting_period=compared_period, group=group
                    )
                except ProdCons.DoesNotExist:
                    compared_prodcons = None

                compared_prod = get_actual_value(
                    compared_prodcons,
                    'calculated_production',
                    group,
                    to_report_groups_compared_period
                )
                compared_cons = get_actual_value(
                    compared_prodcons,
                    'calculated_consumption',
                    group,
                    to_report_groups_compared_period
                )
            else:
                # Comparison with Base year
                compared_prod = get_baseline(
                    main_prodcons,
                    'baseline_prod',
                    main_prod,
                    group
                )
                compared_cons = get_baseline(
                    main_prodcons,
                    'baseline_cons',
                    main_cons,
                    group
                )

            chng_prod = get_chng(main_prod, compared_prod)
            chng_cons = get_chng(main_cons, compared_cons)

            if check_skip_group(
                [main_prod, compared_prod, main_cons, compared_cons]
            ):
                continue

            table_data['data'][group.group_id] = (
                '{id}  - {descr}'.format(
                    id=group.group_id,
                    descr=group.description
                ),
                main_prod,
                compared_prod,
                chng_prod,
                limit_prod,
                main_cons,
                compared_cons,
                chng_cons,
                limit_cons,
                per_capita_cons
            )
        data['tables'].append(table_data)

    return data


def get_actual_value(prodcons, field, group, to_report_groups):
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
    return limit.limit if limit else '-'


def get_per_capita_cons(cons, population):
    if not isinstance(cons, str):
        return round_half_up(cons / population, 4)
    else:
        return '-'


def get_baseline(prodcons, field, actual_value, group):
    if prodcons and getattr(prodcons, field) is not None:
        baseline = getattr(prodcons, field)
    else:
        baseline = 'N.R.'
        if (
            group.group_id in ['CII', 'CIII']
            or (not isinstance(actual_value, str) and actual_value <= 0)
            or actual_value == '-'
        ):
            baseline = ""
    return baseline


def get_chng(actual_value, compared_value):
    if isinstance(actual_value, str) or isinstance(compared_value, str):
        return '-'
    elif actual_value > 0 and compared_value != 0:
        return round_half_up(
            -100 + actual_value / compared_value * 100,
            2
        )
    else:
        return -100


def check_skip_group(values):
    if all(val == '-' or val == "" for val in values):
        return True
    return False
