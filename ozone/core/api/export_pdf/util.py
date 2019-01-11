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


BASIC_Q_TYPES = (
    'Essential use, other than L&A',
    'Critical use',
    'High ambient temperature',
    'Laboratory and analytical',
    'Process agent uses',
    'Other/unspecified'
)


def _p(style_name, align, txt, fontSize=None):
    style = STYLES[style_name]
    style.alignment = align
    if fontSize:
        style.fontSize = fontSize
    return Paragraph(txt, style)


p_c = partial(_p, 'Normal', TA_CENTER, fontSize=FONTSIZE_TABLE)
p_l = partial(_p, 'BodyText', TA_LEFT, fontSize=FONTSIZE_TABLE)

page_title = partial(_p, 'Heading1', TA_CENTER)


def makeBulletList(list):
    bullets=ListFlowable(
        [ListItem(
            _p('BodyText', TA_LEFT, x, fontSize=6),
            leftIndent=35, bulletColor='black', value='circle'
        ) for x in list], bulletType='bullet'
    )
    return bullets

def get_q_label(q_list):
    pairs = tuple(zip(BASIC_Q_TYPES, map(str,q_list)))
    _filtered_pairs = tuple(filter(lambda x: x[1] != '0.0', pairs))

    filtered_pairs = tuple(': '.join(x) for x in _filtered_pairs)

    return makeBulletList(filtered_pairs)
