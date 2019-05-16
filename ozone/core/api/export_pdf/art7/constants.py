from ozone.core.api.export_pdf.util import p_c
from ozone.core.api.export_pdf.util import col_widths

from django.utils.translation import gettext_lazy as _
from reportlab.lib import colors


TABLE_IMPORTS_EXPORTS_HEADER = lambda isBlend, type: (
    (
        p_c(_('Type' if isBlend else 'Annex/Group')),
        p_c(_('Blend' if isBlend else 'Substance')),
        p_c(_(f'{"Exporting" if type=="import" else "Destination"} country/region/territory')),
        p_c(_(f'Total Quantity {type.capitalize()}ed for All Uses')),
        '',
        p_c(_(f'{type.capitalize()} for feedstock')),
        p_c(_(f'Quantity of new substance {type}ed for exempted essential,'
                'critical, high-ambient-temperature or other uses')),
        ''
    ),
    (
        '',
        '',
        '',
        p_c(_('New')),
        p_c(_('Recovered and reclaimed')),
        '',
        p_c(_('Quantity')),
        p_c(_('Decision / type of use or remark')),
    ),
)

TABLE_IMPORTS_EXPORTS_HEADER_STYLE = (
    ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('ALIGN', (0, 2), (5, -1), 'CENTER'),
    ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
    ('SPAN', (0, 0), (0, 1)),
    ('SPAN', (1, 0), (1, 1)),
    ('SPAN', (2, 0), (2, 1)),
    ('SPAN', (3, 0), (4, 0)),
    ('SPAN', (5, 0), (5, 1)),
    ('SPAN', (6, 0), (7, 0)),
)

# TABLE_ROW_EMPTY_IMP_EXP = ((_('No data.'), '', '', '', '', '', '', '',),)

TABLE_ROW_EMPTY_STYLE_IMP_EXP = (
    ('SPAN', (0, 2), (-1, 2)),
    ('VALIGN', (0, 2), (-1, 2), 'MIDDLE'),
    ('ALIGN', (0, 2), (-1, 2), 'CENTER'),
)

TABLE_IMPORTS_EXPORTS_SUBS_WIDTHS = col_widths([1.3, 3, 5, 2, 2, 2, 6, 6])

TABLE_IMPORTS_EXPORTS_BL_WIDTHS = col_widths([3, 3, 3, 2, 2, 2, 6, 6])

TABLE_BLENDS_COMP_STYLE = (
    ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('TOPPADDING', (0, 0), (-1, 0), 10),
)

TABLE_BLENDS_COMP_WIDTHS = col_widths([4, 4, 4, 4, 4, 6])

TABLE_BLENDS_COMP_HEADER = lambda type: (
    (
        p_c(_('Substances')),
        p_c(_('Percentage')),
        p_c(_('Total quantity imported for all uses (new)')),
        p_c(_('Total quantity imported for all uses (recovered and reclaimed)')),
        p_c(_('Quantity of new substance imported for feedstock uses')),
        p_c(_(f'Quantity of new substance {type}ed for exempted essential,'
              'critical, high-ambient-temperature or other uses')),
    ),
)


TABLE_ROW_EMPTY_PROD = ((_('No data.'), '', '', '', '', '', '',),)

TABLE_PROD_HEADER = (
    (
        p_c(_('Annex/Group')),
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
        p_c(_('Annex/Group')),
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

TABLE_PROD_WIDTH = col_widths([1.3, 4, 2, 2, 7, 7, 4])

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
