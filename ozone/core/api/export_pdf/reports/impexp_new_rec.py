from reportlab.lib import colors
from reportlab.platypus import Paragraph, Table, PageBreak, KeepTogether
from reportlab.lib.enums import TA_CENTER

from functools import partial

from django.utils.translation import gettext_lazy as _

from ozone.core.models import (
    Group,
    ProdCons,
    PartyHistory,
)
from ozone.core.models.utils import round_half_up

from ..util import (
    col_widths,
    h1_style,
    b_c, b_r, b_l, smb_c, smb_r, smb_l, smbi_r, smbi_l, sm_no_spacing_style,
    _style,
    FONTSIZE_TABLE, FONTSIZE_H1,
)


page_title_style = _style(
    'Heading1', alignment=TA_CENTER,
    fontSize=FONTSIZE_H1, fontName='Helvetica-Bold',
)
page_title = partial(Paragraph, style=page_title_style)


TABLE_CUSTOM_STYLES = (
    ('FONTSIZE', (0, 0), (-1, -1), FONTSIZE_TABLE),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 0),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ('LEFTPADDING', (0, 0), (-1, -1), 2),
    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ('ALIGN', (1, 3), (-1, -1), 'RIGHT'),
    ('SPAN', (0, 0), (4, 0)),  # Title: Annex III
    ('SPAN', (0, 1), (4, 1)),  # Subtitle
    ('SPAN', (0, 2), (4, 2)),  # Sub-subtitle
    ('SPAN', (1, 4), (2, 4)),  # imports
    ('SPAN', (3, 4), (4, 4)),  # exports
)


TABLE_CUSTOM_KEEPTOGETHER_STYLES = (
    ('FONTSIZE', (0, 0), (-1, -1), FONTSIZE_TABLE),
    ('TOPPADDING', (0, 0), (-1, -1), 0),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ('LEFTPADDING', (0, 0), (-1, -1), 2),
    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
    ('KEEPTOGETHER', (0, 0), (-1, -1)),
)


__all__ = ['get_impexp_new_rec_flowables']


def get_impexp_new_rec_flowables(periods, parties):
    data = get_data(periods, parties)

    flowables = []
    for period_data in data:
        period = period_data['period']
        parties = period_data['parties']
        flowables.append(get_table(period, parties))
        flowables.append(*get_footer())
        flowables.append(Paragraph('', style=h1_style))
        flowables += [PageBreak()]
    return flowables


def get_data(periods, parties):
    data = []
    for period in periods:
        period_data = {
            'period': period.name,
            'parties': []
        }
        for party in parties:
            prodcons_qs = ProdCons.objects.filter(
                party=party,
                reporting_period=period
            )

            groups_data = get_party_data(period, party, prodcons_qs)
            if groups_data['data']:
                if has_subtotal(groups_data['data']):
                    groups_data['data'].append(
                        get_subtotal(period, groups_data['data'])
                    )
                period_data['parties'].append(groups_data)
        data.append(period_data)
    return data


def get_party_data(period, party, prodcons_qs):
    history = PartyHistory.objects.get(
        party=party,
        reporting_period=period
    )

    data = []
    all_groups = Group.objects.all()
    for group in all_groups:
        try:
            prodcons = prodcons_qs.get(group=group)
            import_new = round_half_up(prodcons.import_new, 3)
            import_recovered = round_half_up(prodcons.import_recovered, 3)
            export_new = round_half_up(prodcons.export_new, 3)
            export_recovered = round_half_up(prodcons.export_recovered, 3)
        except ProdCons.DoesNotExist:
            import_new, import_recovered, export_new, export_recovered = 0, 0, 0, 0
        if any([import_new, import_recovered, export_new, export_recovered]) != 0:
            data.append(
                (
                    group.group_id + ' - ' + group.description,
                    import_new,
                    import_recovered,
                    export_new,
                    export_recovered,
                )
            )
    return {
        'name': party.name,
        'population': history.population,
        'party_type': history.party_type.abbr,
        'data': data
    }


def has_subtotal(rows):
    # Don't count Annex F at sub-total
    no_groups = len([group for group in rows if 'HFCs' not in group[0]])

    # Sub-total makes sense when there are at least two groups
    return True if no_groups >= 2 else False


def get_subtotal(period, rows):
    import_new, import_recovered, export_new, export_recovered = 0, 0, 0, 0
    for row in rows:
        # Don't count Annex F when computing the sub-total
        if 'HFCs' in row[0]:
            continue
        import_new += row[1]
        import_recovered += row[2]
        export_new += row[3]
        export_recovered += row[4]
    return (
        smbi_l('Sub-Total ODS for {period} in ODP tonnes'.format(period=period.name)),
        smbi_r(str(round_half_up(import_new, 3))),
        smbi_r(str(round_half_up(import_recovered, 3))),
        smbi_r(str(round_half_up(export_new, 3))),
        smbi_r(str(round_half_up(export_recovered, 3))),
    )


def get_table(period, parties):
    rows = list()
    rows += get_table_header(period)
    styles = list(TABLE_CUSTOM_STYLES)

    for party in parties:
        party_rows = list()
        party_rows.append((
            smb_l(get_party_history(party)),
        ))
        annex_f = None
        for data in party['data']:
            if (not type(data[0]) is Paragraph) and 'HFCs' in data[0]:
                annex_f = data
                continue
            party_rows.append(data)
        if annex_f:
            # We append annex F data after the sub-total
            party_rows.append(annex_f)

        # Append party data as table to use "keeptogether" feature
        styles_keeptogether = list(TABLE_CUSTOM_KEEPTOGETHER_STYLES)
        rows.append(
            (
                Table(
                    party_rows,
                    colWidths=col_widths([8, 2, 3, 2, 3]),
                    style=styles_keeptogether,
                    hAlign='RIGHT'
                ),
                '',
                '',
                '',
                ''
            )
        )
        rows.append(('', '', '', '', ''))

    rows.append(get_total(parties))

    return Table(
        rows,
        repeatRows=6,
        colWidths=col_widths([8, 2, 3, 2, 3]),
        style=styles,
        hAlign='LEFT'
    )


def get_table_header(period):
    return [
        (
            page_title(_('Annex III')),
            '',
            '',
            '',
            '',
        ),
        (
            b_c(
                "{period} Import and export of new and recovered substances".format(
                period=period)
            ),
            '',
            '',
            '',
            '',
        ),
        (
            b_c(
                "(in ODP tonnes for annexes A,B,C,E and CO2-equivalent tonnes for annex F)"
            ),
            '',
            '',
            '',
            '',
        ),
        (
            '',
            '',
            '',
            '',
            '',
        ),
        (
            '',
            smb_c(_('IMPORTS')),
            '',
            smb_c(_('EXPORTS')),
            '',
        ),
        (
            '',
            smb_r(_('New')),
            smb_r(_('Recovered')),
            smb_r(_('New')),
            smb_r(_('Recovered')),
        ),
    ]


def get_title():
    return (
        page_title("Annex III"),
    )


def get_party_history(party):
    return _(
        """{party_name} {party_type} -Population*: {population}""".format(
            party_name=party['name'],
            party_type=party['party_type'],
            population=party['population'],
        )
    )


def get_total(parties):
    import_new, import_recovered, export_new, export_recovered = 0, 0, 0, 0
    for party in parties:
        for row in party['data']:
            if not type(row[0]) is Paragraph:
                import_new += row[1]
                import_recovered += row[2]
                export_new += row[3]
                export_recovered += row[4]
    return (
        b_l('TOTAL'),
        b_r(str(round_half_up(import_new, 3))),
        b_r(str(round_half_up(import_recovered, 3))),
        b_r(str(round_half_up(export_new, 3))),
        b_r(str(round_half_up(export_recovered, 3))),
    )


def get_footer():
    notes = [
        "* Population in thousands",
    ]

    return [
        Paragraph(_(note), sm_no_spacing_style) for note in notes
    ]
