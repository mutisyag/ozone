from .hat_helper import big_table_row
from .hat_helper import TABLE_BLENDS_COMP_HEADER
from .hat_helper import TABLE_BLENDS_COMP_STYLE
from .hat_helper import TABLE_BLENDS_COMP_WIDTHS
from .hat_helper import TABLE_IMPORTS_BL_WIDTHS
from .hat_helper import TABLE_IMPORTS_HEADER
from .hat_helper import TABLE_IMPORTS_HEADER_STYLE
from .hat_helper import TABLE_ROW_EMPTY_STYLE_IMP
from .hat_helper import TABLE_ROW_EMPTY_IMP

from ..util import (
    get_comments_section,
    mk_table_blends,
    mk_table_substances,
    page_title,
    p_c,
    table_from_data,
    to_precision,
    STYLES,
    TABLE_STYLES
)


from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph

from django.utils.translation import gettext_lazy as _


def component_row(component, blend):
    ptg = component.percentage

    return (
        p_c(_(component.substance.name)),
        p_c('<b>{}%</b>'.format(round(ptg * 100, 1))),
        p_c(to_precision(blend.quantity_msac * ptg, 3)),
        p_c(to_precision(blend.quantity_sdac * ptg, 3)),
        p_c(to_precision(blend.quantity_dcpac * ptg, 3)),
    )


def export_imports(submission):
    comments_section = get_comments_section(submission, 'hat_imports')

    grouping = submission.highambienttemperatureimports

    table_substances = tuple(mk_table_substances(grouping, big_table_row))
    table_blends = tuple(mk_table_blends(
        grouping, big_table_row, component_row, TABLE_BLENDS_COMP_HEADER,
        TABLE_BLENDS_COMP_STYLE, TABLE_BLENDS_COMP_WIDTHS
    ))

    style = lambda data: (
        TABLE_IMPORTS_HEADER_STYLE + TABLE_STYLES + (
            () if data else TABLE_ROW_EMPTY_STYLE_IMP
        )
    )

    subst_table = table_from_data(
        data=table_substances, isBlend=False,
        header=TABLE_IMPORTS_HEADER(False, 'import'),
        colWidths=None,
        style=style(table_substances),
        repeatRows=2, emptyData=TABLE_ROW_EMPTY_IMP
    )

    blends_table = table_from_data(
        data=table_blends, isBlend=True,
        header=TABLE_IMPORTS_HEADER(True, 'import'),
        colWidths=TABLE_IMPORTS_BL_WIDTHS,
        style=style(table_blends),
        repeatRows=2, emptyData=TABLE_ROW_EMPTY_IMP
    )

    imports_page = (
        Paragraph(_('1.1 Substances'), STYLES['Heading2']),
        subst_table,
        PageBreak(),
        Paragraph(_('1.2 Blends'), STYLES['Heading2']),
        blends_table,
        PageBreak(),
        Paragraph(_('1.3 Comments'), STYLES['Heading2']),
    )

    return (page_title(_('Consumption (imports)')),) + imports_page + comments_section
