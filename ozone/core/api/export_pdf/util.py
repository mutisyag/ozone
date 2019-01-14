from functools import partial

from reportlab.platypus import Paragraph

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.enums import TA_CENTER

from reportlab.platypus import ListFlowable, ListItem


__all__ = [
    'STYLES',
    'TABLE_STYLES',
    'p_c',
    'p_l',
]


STYLES = getSampleStyleSheet()

FONTSIZE_TABLE = 8

TABLE_STYLES = (
    ('FONTSIZE', (0, 0), (-1, -1), FONTSIZE_TABLE),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
)


TABLE_IMPORTS_EXPORTS_HEADER_STYLE = (
    ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
    ('TOPPADDING', (6,2), (7, -1), 10),
    ('VALIGN', (0, 0), (-1, 1), 'MIDDLE'),
    ('VALIGN', (0, 2), (5, -1), 'MIDDLE'),
    ('VALIGN', (6, 2), (7, -1), 'TOP'),
    ('ALIGN', (0, 2), (5, -1), 'CENTER'),
    ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
    ('SPAN', (0, 0), (0, 1)),
    ('SPAN', (1, 0), (1, 1)),
    ('SPAN', (2, 0), (2, 1)),
    ('SPAN', (3, 0), (4, 0)),
    ('SPAN', (5, 0), (5, 1)),
    ('SPAN', (6, 0), (7, 0)),
)




def _p(style_name, align, txt, fontSize=None, fontName=None):
    style = STYLES[style_name]
    style.alignment = align
    if fontSize:
        style.fontSize = fontSize
    if fontName:
        style.fontName = fontName
    return Paragraph(txt, style)


p_c = partial(_p, 'Normal', TA_CENTER, fontSize=FONTSIZE_TABLE)
p_l = partial(_p, 'BodyText', TA_LEFT, fontSize=FONTSIZE_TABLE)

page_title = partial(_p, 'Heading1', TA_CENTER)


BASIC_Q_TYPES = (
    'Essential use, other than L&amp;A',
    'Critical use',
    'High ambient temperature',
    'Laboratory and analytical',
    'Process agent uses',
    'Other/unspecified'
)

def makeBulletList(list, fontSize):
    bullets=ListFlowable(
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
    pairs = tuple(zip(BASIC_Q_TYPES, map(str,q_list)))

    if type=='quantity':
        _filtered_pairs = tuple(filter(lambda x: x[1] != '0.0', pairs))
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
        obj.decision_essential_uses,
        obj.decision_critical_uses,
        obj.decision_high_ambient_temperature,
        obj.decision_laboratory_analytical_uses,
        obj.decision_process_agent_uses,
        obj.decision_other_uses,
    )
