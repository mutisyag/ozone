import re

from copy import deepcopy
from collections import OrderedDict
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from functools import partial

from reportlab.platypus import ListFlowable
from reportlab.platypus import ListItem
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus import Table
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.units import mm


__all__ = [
    'hr',
    'page_title_section',
    'page_title',
    'p_c',
    'p_l',
    'p_r',
    'b_c',
    'b_l',
    'b_r',
    'sm_c',
    'sm_l',
    'sm_r',
    'smb_c',
    'smb_l',
    'smb_r',
    'p_bullet',
]


STYLES = getSampleStyleSheet()

FONTSIZE_SMALL = 7
FONTSIZE_DEFAULT = 8
FONTSIZE_TABLE = FONTSIZE_SMALL
FONTSIZE_BULLET_LIST = FONTSIZE_DEFAULT - 1
FONTSIZE_H3 = FONTSIZE_DEFAULT + 2
FONTSIZE_H2 = FONTSIZE_H3 + 3
FONTSIZE_H1 = FONTSIZE_H2 + 3

grid_color = (0.4, 0.4, 0.4)
soft_color = (0.8, 0.8, 0.8)
lighter_grey = (0.95, 0.95, 0.95)


TABLE_STYLES = (
    ('FONTSIZE', (0, 0), (-1, -1), FONTSIZE_TABLE),
    ('GRID', (0, 0), (-1, 0), 0.5, grid_color),
    ('BOX', (0, 0), (-1, -1), 0.5, grid_color),
    ('LINEBEFORE', (0, 0), (-1, -1), 0.1, soft_color),
    ('LINEABOVE', (0, 0), (-1, -1), 0.1, grid_color),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('TOPPADDING', (0, 0), (-1, -1), 0),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ('LEFTPADDING', (0, 0), (-1, -1), 2),
    ('RIGHTPADDING', (0, 0), (-1, -1), 2),
)

DOUBLE_HEADER_TABLE_STYLES = TABLE_STYLES + (
    ('GRID', (0, 0), (-1, 1), 0.5, grid_color),
    ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
    ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
)

SINGLE_HEADER_TABLE_STYLES = TABLE_STYLES + (
    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
)


def _style(style_name, **kwargs):
    style = deepcopy(STYLES[style_name])
    if kwargs is not None:
        for k, v in kwargs.items():
            setattr(style, k, v)
    return style


hr = HRFlowable(
    width="100%", thickness=1, lineCap='round', color=colors.lightgrey,
    spaceBefore=1, spaceAfter=1, hAlign='CENTER', vAlign='BOTTOM', dash=None
)

_bodytext = partial(_style, 'BodyText', fontSize=FONTSIZE_DEFAULT, fontName='Helvetica')

centered_paragraph_style = _bodytext(alignment=TA_CENTER)
left_paragraph_style = _bodytext(alignment=TA_LEFT)
right_paragraph_style = _bodytext(alignment=TA_RIGHT)
bold_centered_paragraph_style = _bodytext(alignment=TA_CENTER, fontName='Helvetica-Bold')
bold_left_paragraph_style = _bodytext(alignment=TA_LEFT, fontName='Helvetica-Bold')
bold_right_paragraph_style = _bodytext(alignment=TA_RIGHT, fontName='Helvetica-Bold')
small_centered_paragraph_style = _bodytext(alignment=TA_CENTER, fontSize=FONTSIZE_SMALL)
small_left_paragraph_style = _bodytext(alignment=TA_LEFT, fontSize=FONTSIZE_SMALL)
small_right_paragraph_style = _bodytext(alignment=TA_RIGHT, fontSize=FONTSIZE_SMALL)
small_bold_centered_paragraph_style = _bodytext(alignment=TA_CENTER, fontSize=FONTSIZE_SMALL, fontName='Helvetica-Bold')
small_bold_left_paragraph_style = _bodytext(alignment=TA_LEFT, fontSize=FONTSIZE_SMALL, fontName='Helvetica-Bold')
small_bold_right_paragraph_style = _bodytext(alignment=TA_RIGHT, fontSize=FONTSIZE_SMALL, fontName='Helvetica-Bold')
bullet_paragraph_style = _bodytext(alignment=TA_LEFT)
no_spacing_style = _bodytext(alignment=TA_LEFT, spaceBefore=0)


left_description_style = _style('BodyText', alignment=TA_LEFT, fontSize=FONTSIZE_SMALL, spaceBefore=-1)

h1_style = _style(
    'Heading1',
    alignment=TA_CENTER,
    fontSize=FONTSIZE_DEFAULT+6,
    fontName='Helvetica-Bold',
)

h2_style = _style(
    'Heading2',
    alignment=TA_LEFT,
    fontSize=FONTSIZE_DEFAULT+4,
    fontName='Helvetica-Bold',
)

h3_style = _style(
    'Heading3',
    alignment=TA_LEFT,
    fontSize=FONTSIZE_DEFAULT+2,
    fontName='Helvetica-Bold',
    spaceBefore=0
)

page_title_style = _style(
    'Heading3', alignment=TA_LEFT,
    fontSize=FONTSIZE_H3, fontName='Helvetica-Bold',
)

p_c = partial(Paragraph, style=centered_paragraph_style)
p_l = partial(Paragraph, style=left_paragraph_style)
p_r = partial(Paragraph, style=right_paragraph_style)

b_c = partial(Paragraph, style=bold_centered_paragraph_style)
b_l = partial(Paragraph, style=bold_left_paragraph_style)
b_r = partial(Paragraph, style=bold_right_paragraph_style)

sm_c = partial(Paragraph, style=small_centered_paragraph_style)
sm_l = partial(Paragraph, style=small_left_paragraph_style)
sm_r = partial(Paragraph, style=small_right_paragraph_style)

smb_c = partial(Paragraph, style=small_bold_centered_paragraph_style)
smb_l = partial(Paragraph, style=small_bold_left_paragraph_style)
smb_r = partial(Paragraph, style=small_bold_right_paragraph_style)

p_bullet = partial(Paragraph, style=bullet_paragraph_style)
page_title = partial(Paragraph, style=page_title_style)


# TODO: remove this after revising HAT exports
def page_title_section(title, explanatory=None):
    return (
        page_title(title),
        # p_c(explanatory, fontSize=10),
        # Spacer(1, cm),
    )


def col_widths(w_list):
    return list(map(lambda x: x * cm, w_list))


# Returning number as string to avoid 'E' notation
def get_big_float(nr):
    if not nr:
        return ''
    return '{:f}'.format(Decimal(str(nr)))


def as_decimal(nr):
    if not nr:
        return None
    if not isinstance(nr, Decimal):
        return Decimal(repr(nr))
    return nr


def sum_decimals(d1, d2):
    dd1 = as_decimal(d1)
    dd2 = as_decimal(d2)
    if dd1 and dd2:
        return dd1+dd2
    return dd1 or dd2


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


EXEMPTED_FIELDS = OrderedDict([
    ('laboratory_analytical_uses', _('Laboratory and analytical uses')),
    ('essential_uses', _('Essential uses, other than L&A')),
    ('critical_uses', _('Critical uses')),
    ('high_ambient_temperature', _('High ambient temperature')),
    ('process_agent_uses', _('Process agent uses')),
    ('other_uses', _('Other/unspecified uses')),
])


def get_quantity(obj, field):
    """
    field is a key in EXEMPTED_FIELDS
    """
    return getattr(obj, 'quantity_' + field) if field else None


def get_decision(obj, field):
    """
    field is a key in EXEMPTED_FIELDS
    """
    return getattr(obj, 'decision_' + field) if field else None


def get_substance_or_blend_name(obj):
    return (
        obj.substance.name
        if obj.substance
        else '%s - %s' % (
            obj.blend.blend_id,
            obj.blend.composition
        )
    )


def get_group_name(obj):
    return (
        obj.substance.group.name
        if obj.substance and obj.substance.group
        else ''
    )


def rows_to_table(header, rows, colWidths, style):
    return Table(
        header + rows,
        colWidths=colWidths,
        style=style,
        hAlign='LEFT',
        repeatRows=len(header)  # repeat header on page break
    ) if rows else None


def exclude_blend_items(data):
    return data.exclude(blend_item__isnull=False)


def get_remarks(item):
    if not item.remarks_party:
        return item.remarks_os or ''
    else:
        if not item.remarks_os:
            return item.remarks_party
        else:
            return '%s<br/>%s' % (item.remarks_party, item.remarks_os)


def get_comments_section(submission, type):
    r_party = getattr(submission, type + '_remarks_party')
    r_secretariat = getattr(submission, type + '_remarks_secretariat')

    remarks_party = p_l('%s (%s): %s' % (
        _('Comments'), _('party'), r_party
    ))
    remarks_secretariat = p_l('%s (%s): %s' % (
        _('Comments'), _('secretariat'), r_secretariat
    ))
    return (
        remarks_party if r_party else None,
        remarks_secretariat if r_secretariat else None,
    )


#  Not used, but kept just in case we need bulleted lists
def makeBulletList(list):
    bullets = ListFlowable(
        [
            ListItem(
                p_bullet(x),
                leftIndent=10, bulletColor='black', value='circle',
                bulletOffsetY=-2.88
            ) for x in list
        ],
        bulletType='bullet', bulletFontSize=3, leftIndent=5
    )

    return bullets


# TODO: remove this after revising HAT exports
def table_from_data(
    data, isBlend, header, colWidths, style, repeatRows, emptyData=None
):

    if not data and not emptyData:
        # nothing at all unless explicitly requested
        return ()
    if not data:
        # Just a text, without a table heading
        return (p_l(emptyData))
    # Spanning all columns for the blend components rows
    if isBlend:
        rows = len(data) + repeatRows
        for row_idx in range(repeatRows+1, rows, 2):
            style += (
                ('SPAN', (0, row_idx), (-1, row_idx)),
                ('ALIGN', (0, row_idx), (-1, row_idx), 'CENTER')
            )

    return Table(
        header + data,
        colWidths=colWidths,
        style=style,
        hAlign='LEFT',
        repeatRows=2  # repeat header on page break
    )


# TODO: remove this after revising HAT exports
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
                 Table(header + data, style=style, colWidths=widths),
                 Spacer(7, mm)),
                )
        )

    return result


# TODO: remove this after revising HAT exports
def mk_table_substances(grouping, row_fct):
    # Excluding items with no substance,
    # then getting the ones that are not a blend
    objs = grouping.exclude(substance=None).filter(blend_item=None)
    row = partial(row_fct, isBlend=False)
    return map(row, objs)


# TODO: remove this after revising HAT exports
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


def get_date_of_reporting_str(submission):
    date_of_reporting = submission.submitted_at or submission.info.date
    if date_of_reporting:
        date_of_reporting = date_of_reporting.strftime('%d %B %Y')
    return date_of_reporting


def get_compared_period(periods):
    if len(periods) == 1:
        # Comparison with Base year
        periods.append(
            DottedDict({'name': 'Base'})
        )
    return periods


class DottedDict(object):
    """
    Helper class for accessing dictionary items as object attributes.
    """
    def __init__(self, d):
        self.__dict__ = d
