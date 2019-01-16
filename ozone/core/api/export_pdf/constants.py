from .util import FONTSIZE_TABLE
from .util import p_c

from django.utils.translation import gettext_lazy as _

from reportlab.lib import colors
from reportlab.lib.units import cm


TABLE_STYLES = (
    ('FONTSIZE', (0, 0), (-1, -1), FONTSIZE_TABLE),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
)

TABLE_IMPORTS_EXPORTS_HEADER_STYLE = (
    ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
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

TABLE_ROW_EMPTY_IMP_EXP = (
    (
        _('No data.'),
        '',
        '',
        '',
        '',
        '',
        '',
        '',
    ),
)

TABLE_ROW_EMPTY_STYLE_IMP_EXP = (
    ('SPAN', (0, 2), (-1, 2)),
    ('VALIGN', (0, 2), (-1, 2), 'MIDDLE'),
    ('ALIGN', (0, 2), (-1, 2), 'CENTER'),
)

TABLE_IMPORTS_EXPORTS_SUBS_WIDTHS = list(
    map(lambda x: x * cm, [1.3, 2.1, 4, 2, 2, 2, 7, 7])
)

TABLE_IMPORTS_EXPORTS_BL_WIDTHS = list(
    map(lambda x: x * cm, [3, 3, 3, 2, 2, 2, 6, 6])
)


TABLE_BLENDS_COMP_STYLE = (
    ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('TOPPADDING', (0, 0), (-1, 0), 10),
)

TABLE_BLENDS_COMP_WIDTHS = list(
    map(lambda x: x * cm, [4, 4, 4, 4, 4, 6])
)

TABLE_BLENDS_COMP_HEADER = (
    (
        p_c(_('Substances')),
        p_c(_('Percentage')),
        p_c(_('Total quantity imported for all uses (new)')),
        p_c(_('Total quantity imported for all uses (recovered and reclaimed)')),
        p_c(_('Quantity of new substances imported as feedstock')),
        p_c(_('Quantity of new substance imported for exempted essential,'
              'critical, high-ambient-temperature or other uses')),
    ),
)

