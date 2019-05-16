from ozone.core.api.export_pdf.util import p_c
from ozone.core.api.export_pdf.util import col_widths
from ozone.core.api.export_pdf.util import FONTSIZE_TABLE

from django.utils.translation import gettext_lazy as _
from reportlab.lib import colors


TABLE_INFO_WIDTHS = col_widths([2.5] * 6 + [1]*10)
TABLE_INFO_HEADER = (
    (
        p_c('Questionnaire'), '', '', '', '', '',
        p_c(_('Annex/Group reported in full?')),
    ),
    (
        p_c(_('Imports')),
        p_c(_('Exports')),
        p_c(_('Production')),
        p_c(_('Destruction')),
        p_c(_('Non-party trade')),
        p_c(_('Emissions')),
        p_c(_('A/I')),
        p_c(_('A/II')),
        p_c(_('B/I')),
        p_c(_('B/II')),
        p_c(_('B/III')),
        p_c(_('C/I')),
        p_c(_('C/II')),
        p_c(_('C/III')),
        p_c(_('E/I')),
        p_c(_('F')),
    ),
)
TABLE_INFO_STYLE = (
    ('FONTSIZE', (0, 0), (-1, -1), FONTSIZE_TABLE),
    ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.grey),
    ('BOX', (0, 0), (5, 2), 0.5, colors.grey),
    ('BOX', (6, 0), (15, 2), 0.5, colors.grey),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('SPAN', (0, 0), (5, 0)),
    ('SPAN', (6, 0), (15, 0)),
)

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
        p_c(_('Type' if isBlend else 'Annex/Group')),
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

TABLE_DEST_WIDTH = col_widths([4, 3, 4, 6, 6])

TABLE_DEST_COMP_WIDTH = col_widths([6, 5, 6])


TABLE_NONP_HEADER = lambda isBlend: (
        (
            p_c(_('Type' if isBlend else 'Annex/Group')),
            p_c(_('Blend' if isBlend else 'Substance')),
            p_c(_('Exporting or destination country/region/territory')),
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
    ('SPAN', (5, 0), (6, 0)),
    ('SPAN', (7, 0), (7, 1)),
    ('SPAN', (8, 0), (8, 1)),
)

TABLE_NONP_SUBS_WIDTHS = col_widths([2, 3, 4, 2, 2, 2, 2, 4, 4])

TABLE_NONP_COMP_WIDTHS = col_widths([4, 3, 3, 3, 3, 3])


TABLE_EMISSIONS_HEADER = (
    (
        p_c(_('Facility name or identifier')),
        p_c(_('Total amount generated')),
        p_c(_('Amount generated and captured')),
        '',
        '',
        p_c(_('Amount used for feedstock without prior capture')),
        p_c(_('Amount destroyed without prior capture')),
        p_c(_('Amount of generated emissions')),
        p_c(_('Remarks (party)')),
        p_c(_('Remarks (secretariat)')),
    ),
    (
        '',
        '',
        p_c(_('For all uses')),
        p_c(_('For feedstock use in your country')),
        p_c(_('For destruction')),
        '',
        '',
        '',
        '',
        '',
    )
)

TABLE_EMISSIONS_HEADER_STYLE = (
    ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
    ('ALIGN', (0, 2), (7, -1), 'CENTER'),
    ('SPAN', (0, 0), (0, 1)),
    ('SPAN', (1, 0), (1, 1)),
    ('SPAN', (2, 0), (4, 0)),
    ('SPAN', (5, 0), (5, 1)),
    ('SPAN', (6, 0), (6, 1)),
    ('SPAN', (7, 0), (7, 1)),
    ('SPAN', (8, 0), (8, 1)),
    ('SPAN', (9, 0), (9, 1)),
)

TABLE_ROW_EMPTY_EMISSIONS = (
    (_('No data.'), '', '', '', '', '', '', '', '', ''),
)
