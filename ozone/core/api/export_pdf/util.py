from functools import partial

from reportlab.platypus import Paragraph

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.enums import TA_CENTER


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


def _p(style_name, align, txt, fontSize=None):
    style = STYLES[style_name]
    style.alignment = align
    if fontSize:
        style.fontSize = fontSize
    return Paragraph(txt, style)


p_c = partial(_p, 'Normal', TA_CENTER, fontSize=FONTSIZE_TABLE)
p_l = partial(_p, 'BodyText', TA_LEFT, fontSize=FONTSIZE_TABLE)

page_title = partial(_p, 'Heading1', TA_CENTER)
