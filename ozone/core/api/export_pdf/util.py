import re

from django.utils.translation import gettext_lazy as _
from functools import partial

from reportlab.platypus import ListFlowable
from reportlab.platypus import ListItem
from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus import Table
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.units import mm


__all__ = [
    'get_decisions',
    'get_preship_or_polyols_q',
    'get_quantities',
    'get_quantity_cell',
    'hr',
    'page_title_section',
    'p_c',
    'p_l',
    'STYLES'
]


STYLES = getSampleStyleSheet()
FONTSIZE_TABLE = 8

TABLE_STYLES = (
    ('FONTSIZE', (0, 0), (-1, -1), FONTSIZE_TABLE),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
)


def _p(style_name, align, txt, fontSize=None, fontName=None):
    style = STYLES[style_name]
    style.alignment = align
    if fontSize:
        style.fontSize = fontSize
    if fontName:
        style.fontName = fontName
    return Paragraph(txt, style)


hr = HRFlowable(
    width="100%", thickness=1, lineCap='round', color=colors.lightgrey,
    spaceBefore=1, spaceAfter=1, hAlign='CENTER', vAlign='BOTTOM', dash=None
)

p_c = partial(_p, 'Normal', TA_CENTER, fontSize=FONTSIZE_TABLE)
p_l = partial(_p, 'BodyText', TA_LEFT, fontSize=FONTSIZE_TABLE)

page_title = partial(_p, 'Heading1', TA_CENTER)


def page_title_section(title, explanatory):
    return (
        page_title(title),
        p_c(explanatory, fontSize=10),
        Spacer(1, cm),
    )


def col_widths(w_list):
    return list(map(lambda x: x * cm, w_list))


# Returning number as string to avoid 'E' notation
def get_big_float(nr):
    if 'e' in str(nr):
        n, exp = str(nr).split('e')
        s_n = str(float(n)/10)

        idx = s_n.index('.')
        return s_n[:idx+1] + '0' * (int(exp[-1])-1) + s_n[idx+1:]
    else:
        return str(nr)


# Imitate JavaScript's toPrecision. Retunrning the number with 'decimals'
# digits starting from the first non-zero digit
def to_precision(nr, decimals):

    if int(nr) > 999:
        return str(int(nr))
    else:
        s_nr = get_big_float(nr)

        # Getting the first non-zero digitindex
        p = re.compile('(?=\d)(?=[^0])')

        m = p.search(s_nr)
        f_nonzero = m.span()[0]

        # Complete the number with 0's to have space for nr of decimals
        if len(s_nr) <= f_nonzero + decimals:
            nr = s_nr[0:f_nonzero] + s_nr[f_nonzero:]
            return nr
        else:
            # Checking if substring with the number of decimals
            # has a float point
            if '.' not in s_nr[f_nonzero:f_nonzero + decimals]:
                sub = s_nr[f_nonzero:f_nonzero + decimals]
                next_digit = s_nr[f_nonzero + decimals]

                # In case of numbers with 3 digits before the point
                if next_digit == '.':
                    next_digit = s_nr[f_nonzero + decimals + 1]
            else:
                sub = s_nr[f_nonzero:f_nonzero + decimals + 1]
                # For numbers that start wih a non-zero and have exactly
                # 'decimals' digits
                if len(sub) == len(s_nr):
                    next_digit = 0
                else:
                    next_digit = s_nr[f_nonzero + decimals + 1]

            # Concatenating the string before the first non-zero digit
            n = s_nr[0:f_nonzero] + sub

            # Rounding if the next digit after the number of decimals
            # is greater or equal to 5
            if int(next_digit) >= 5:
                # If the point comes after the number of decimals, the number
                # gets rounded with 1
                if s_nr.find(sub) < s_nr.find('.'):
                    add_with = '1'
                else:
                    # Rounding with the correct value depending of the decimals
                    add_with = '0.' + '0' * len(n[n.find('.') + 1: -1])+'1'

                n = str(round(float(n) + float(add_with), 10))

            # Getting rid of the 'E' notation
            if 'e' in n:
                return get_big_float(n)
            return n


BASIC_Q_TYPES = (
    'Essential use, other than L&amp;A',
    'Critical use',
    'High ambient temperature',
    'Laboratory and analytical',
    'Process agent uses',
    'Other/unspecified'
)


def get_quantity_cell(q_list, extra_q):
    if sum(q_list) > 0:
        if extra_q:
            return (
                p_l('<b>' + get_big_float(str(sum(q_list))) + '</b>'),
                get_substance_label(q_list, type='quantity'), hr, extra_q
            )
        else:
            return (
                p_l('<b>' + get_big_float(str(sum(q_list))) + '</b>'),
                get_substance_label(q_list, type='quantity')
            )
    else:
        return ''


def makeBulletList(list, fontSize):
    bullets = ListFlowable(
        [
            ListItem(
                _p('BodyText', TA_LEFT, x, fontSize=fontSize),
                leftIndent=10, bulletColor='black', value='circle',
                bulletOffsetY=-2.88
            ) for x in list
        ],
        bulletType='bullet', bulletFontSize=3, leftIndent=5
    )

    return bullets


def get_substance_label(q_list, type, list_font_size=7):
    # Adding the extra pre-shipment decision
    if type == 'decision':
        pairs = tuple(zip(
            ('Quarantine and pre-shipment applications', ) + BASIC_Q_TYPES,
            q_list
        ))
    else:
        pairs = tuple(zip(
            BASIC_Q_TYPES, map(get_big_float, q_list)
        ))

    if type == 'quantity':
        _filtered_pairs = tuple(filter(lambda x: x[1] != '0', pairs))
    else:
        _filtered_pairs = tuple(filter(lambda x: x[1] != '', pairs))

    filtered_pairs = tuple(': '.join(x) for x in _filtered_pairs)

    return makeBulletList(filtered_pairs, list_font_size)


def get_quantities(obj):
    return (
        obj.quantity_essential_uses or 0,
        obj.quantity_critical_uses or 0,
        obj.quantity_high_ambient_temperature or 0,
        obj.quantity_laboratory_analytical_uses or 0,
        obj.quantity_process_agent_uses or 0,
        obj.quantity_other_uses or 0,
    )


def get_decisions(obj):
    return (
        obj.decision_quarantine_pre_shipment,
        obj.decision_essential_uses,
        obj.decision_critical_uses,
        obj.decision_high_ambient_temperature,
        obj.decision_laboratory_analytical_uses,
        obj.decision_process_agent_uses,
        obj.decision_other_uses,
    )


def get_preship_or_polyols_q(obj):
    _q_pre_ship = obj.quantity_quarantine_pre_shipment
    _q_polyols = obj.quantity_polyols if hasattr(
        obj, 'quantity_polyols') else None

    if _q_pre_ship:
        substance = obj.substance
        return (
            p_l(f'<b>Quantity of new {substance.name} '
                'imported to be used for QPS applications</b>'),
            p_l(str(_q_pre_ship)),
        )

    if _q_polyols:
        return (
            p_l('<b>Polyols quantity</b>'),
            p_l(str(_q_polyols)),
        )

    return None


def table_from_data(
    data, isBlend, header, colWidths, style, repeatRows, emptyData
):

    # Spanning all columns for the blend components rows
    if isBlend:
        rows = len(data) + repeatRows
        for row_idx in range(repeatRows+1, rows, 2):
            style += (
                ('SPAN', (0, row_idx), (-1, row_idx)),
                ('ALIGN', (0, row_idx), (-1, row_idx), 'CENTER')
            )

    return Table(
        header + (data or emptyData),
        colWidths=colWidths,
        style=style,
        repeatRows=2  # repeat header on page break
    )


def table_with_blends(blends, grouping, make_component, header, style, widths):
    result = []

    for blend_row in blends:
        # Getting the blend object based on the id
        blend = grouping.filter(blend__blend_id=blend_row[1].text).first()
        row_comp = partial(make_component, blend=blend)
        data = tuple(map(row_comp, blend.blend.components.all()))

        result.append(blend_row)
        result.append(
            (
                (Spacer(7, mm),
                 Table(
                     header + data,
                     style=style,
                     colWidths=widths,
                 ),
                 Spacer(7, mm))
                ,)
        )

    return result


def mk_table_substances(grouping, row_fct):
    # Excluding items with no substance,
    # then getting the ones that are not a blend
    objs = grouping.exclude(substance=None).filter(blend_item=None)
    row = partial(row_fct, isBlend=False)
    return map(row, objs)


def mk_table_blends(grouping, row_fct, comp_fct, c_header, c_style, c_widths):
    objs = grouping.filter(substance=None)
    row = partial(row_fct, isBlend=True)

    blends = map(row, objs)

    return table_with_blends(
        blends=blends,
        grouping=grouping,
        make_component=comp_fct,
        header=c_header,
        style=c_style,
        widths=c_widths
    )


def get_comments_section(submission, type):
    r_party = getattr(submission, type + '_remarks_party')
    r_secretariat = getattr(submission, type + '_remarks_secretariat')

    return (
        Paragraph(_('Comments (Party)'), STYLES['Heading3']),
        hr,
        p_l(_(r_party if r_party else 'No comments (party)')),
        Spacer(1, cm),
        Paragraph(_('Comments (Secretariat)'), STYLES['Heading3']),
        hr,
        p_l(_(r_secretariat if r_secretariat else 'No comments (secretariat)')),
        PageBreak()
    )
