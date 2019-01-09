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


TABLE_STYLES = (
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
)


def _p(style_name, align, txt):
    style = STYLES[style_name]
    style.alignment = align
    return Paragraph(txt, style)


p_c = partial(_p, 'BodyText', TA_CENTER)
p_l = partial(_p, 'BodyText', TA_LEFT)