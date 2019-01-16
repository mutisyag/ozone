from functools import partial

from reportlab.platypus import ListFlowable
from reportlab.platypus import ListItem
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus.flowables import HRFlowable


from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm


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
    ('VALIGN', (0, 2), (7, -1), 'MIDDLE'),
    ('ALIGN', (0, 2), (5, -1), 'CENTER'),
    ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
    ('SPAN', (0, 0), (0, 1)),
    ('SPAN', (1, 0), (1, 1)),
    ('SPAN', (2, 0), (2, 1)),
    ('SPAN', (3, 0), (4, 0)),
    ('SPAN', (5, 0), (5, 1)),
    ('SPAN', (6, 0), (7, 0)),
)

TABLE_IMPORTS_EXPORTS_SUBS_WIDTHS = list(
    map(lambda x: x * cm, [1.3, 2.1, 4, 2, 2, 2, 7, 7])
)

TABLE_IMPORTS_EXPORTS_BL_WIDTHS = list(
    map(lambda x: x * cm, [3, 3, 3, 2, 2, 2, 6, 6])
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
                p_l('<b>' + str(sum(q_list)) + '</b>'),
                get_substance_label(q_list, type='quantity'), hr, extra_q
            )
        else:
            return (
                p_l('<b>' + str(sum(q_list)) + '</b>'),
                get_substance_label(q_list, type='quantity')
            )
    else:
        return ''

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
    # Adding the extra pre-shipment decision
    if type=='decision':
        pairs = tuple(zip(
            ('Quarantine and pre-shipment applications', ) + BASIC_Q_TYPES,
            map(str, q_list)
        ))
    else:
        pairs = tuple(zip(BASIC_Q_TYPES, map(str, q_list)))

    if type=='quantity':
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
    _q_polyols = obj.quantity_polyols if hasattr(obj, 'quantity_polyols') else None

    substance = obj.substance

    if _q_pre_ship:
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
