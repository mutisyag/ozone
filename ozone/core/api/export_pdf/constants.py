from .util import p_c

from django.utils.translation import gettext_lazy as _

from reportlab.lib import colors
from reportlab.lib.units import cm


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

TABLE_ROW_EMPTY_IMP_EXP = ((_('No data.'), '', '', '', '', '', '', '',),)

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


TABLE_ROW_EMPTY_PROD = ((_('No data.'), '', '', '', '', '', '',),)

TABLE_PROD_HEADER = (
    (
        p_c(_('Group')),
        p_c(_('Substance')),
        p_c(_('Total production for all uses')),
        p_c(_('Production for feedstock uses within your country')),
        p_c(_('Production for exempted essential, '
              'critical or other uses within your country')),
        '',
        p_c(_('Production for supply to Article 5 countries in '
              'accordance with Articles 2A 2H and 5')),
    ),
    (
        '',
        '',
        '',
        '',
        p_c(_('Quantity')),
        p_c(_('Decision / type of use')),
        '',
    ),
)

TABLE_PROD_HEADER_FII = (
    (
        p_c(_('Group')),
        p_c(_('Substance')),
        p_c(_('Captured for all uses')),
        p_c(_('Captured for feedstock uses within your country')),
        p_c(_('Captured for destruction')),
        p_c(_('Production for exempted essential, '
              'critical or other uses within your country')),
        '',
    ),
    (
        '',
        '',
        '',
        '',
        '',
        p_c(_('Quantity')),
        p_c(_('Decision / type of use')),
    ),
)

TABLE_PROD_WIDTH = list(map(lambda x: x * cm, [1.3, 4, 2, 2, 7, 7, 4]))

TABLE_PROD_HEADER_STYLE = (
    ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
    ('VALIGN', (0, 0), (-1, 1), 'MIDDLE'),
    ('VALIGN', (0, 2), (3, -1), 'MIDDLE'),
    ('VALIGN', (5, 2), (6, -1), 'MIDDLE'),
    ('ALIGN', (0, 2), (3, -1), 'CENTER'),
    ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
    ('ALIGN', (6, 2), (6, -1), 'CENTER'),
    ('SPAN', (0, 0), (0, 1)),
    ('SPAN', (1, 0), (1, 1)),
    ('SPAN', (2, 0), (2, 1)),
    ('SPAN', (3, 0), (3, 1)),
    ('SPAN', (4, 0), (5, 0)),
    ('SPAN', (6, 0), (6, 1)),
)

TABLE_PROD_HEADER_STYLE_FII = (
    ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
    ('VALIGN', (0, 0), (-1, 1), 'MIDDLE'),
    ('SPAN', (0, 0), (0, 1)),
    ('SPAN', (1, 0), (1, 1)),
    ('SPAN', (2, 0), (2, 1)),
    ('SPAN', (3, 0), (3, 1)),
    ('SPAN', (4, 0), (4, 1)),
    ('SPAN', (5, 0), (6, 0)),
)


TABLE_ROW_EMPTY_DEST = ((_('No data.'), '', '', '', '',),)

TABLE_ROW_EMPTY_STYLE_DEST = (
    ('SPAN', (0, 1), (-1, 1)),
    ('VALIGN', (0, 1), (-1, 1), 'MIDDLE'),
    ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
)

TABLE_DEST_HEADER_STYLE = (
    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
    ('ALIGN', (0, 1), (2, -1), 'CENTER'),
)

TABLE_DEST_COMP_HEADER = (
    (
        p_c(_('Substances')),
        p_c(_('Percentage')),
        p_c(_('Quantity destroyed')),
    ),
)

TABLE_DEST_HEADER = lambda isBlend: (
    (
        p_c(_('Type' if isBlend else 'Group')),
        p_c(_('Blend' if isBlend else 'Substance')),
        p_c(_('Quantity destroyed')),
        p_c(_('Remarks (party)')),
        p_c(_('Remarks (secretariat)')),
    ),
)

TABLE_NONP_COMP_HEADER = (
    (
        p_c(_('Substances')),
        p_c(_('Percentage')),
        p_c(_('Quantity of imports from non-parties (new)')),
        p_c(_('Quantity of imports from non-parties (recovered)')),
        p_c(_('Quantity of exports from non-parties (new)')),
        p_c(_('Quantity of exports from non-parties (recovered)')),
    ),
)

TABLE_DEST_WIDTH = list(map(lambda x: x * cm, [4, 3, 4, 6, 6]))

TABLE_DEST_COMP_WIDTH = list(map(lambda x: x * cm, [6, 5, 6]))


TABLE_NONP_HEADER = lambda isBlend: (
        (
            p_c(_('Type' if isBlend else 'Group')),
            p_c(_('Blend' if isBlend else 'Substance')),
            p_c(_('Exporting party for quantities reported as imports <b>OR</b> Country of destination of exports')),
            p_c(_('Quantity of imports from non-parties')),
            '',
            p_c(_('Quantity of exports from non-parties')),
            '',
            p_c(_('Remarks (party)')),
            p_c(_('Remarks (secretariat)')),
        ),
        (
            '',
            '',
            '',
            p_c(_('New imports')),
            p_c(_('Recovered and reclaimed imports')),
            p_c(_('New exports')),
            p_c(_('Recovered and reclaimed exports')),
            '',
            '',
        )
    )

TABLE_ROW_EMPTY_NONP = ((_('No data.'), '', '', '', '', '', '', '', ''),)

TABLE_NONP_HEADER_STYLE = (
    ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
    ('ALIGN', (0, 2), (6, -1), 'CENTER'),
    ('SPAN', (0, 0), (0, 1)),
    ('SPAN', (1, 0), (1, 1)),
    ('SPAN', (2, 0), (2, 1)),
    ('SPAN', (3, 0), (4, 0)),
    ('SPAN', (3, 0), (4, 0)),
    ('SPAN', (5, 0), (6, 0)),
    ('SPAN', (7, 0), (7, 1)),
    ('SPAN', (8, 0), (8, 1)),
)

TABLE_NONP_SUBS_WIDTHS = list(
    map(lambda x: x * cm, [2, 3, 4, 2, 2, 2, 2, 4, 4])
)

TABLE_NONP_COMP_WIDTHS = list(
    map(lambda x: x * cm, [4, 3, 3, 3, 3, 3])
)


