from ..constants import TABLE_BLENDS_COMP_HEADER
from ..constants import TABLE_BLENDS_COMP_STYLE
from ..constants import TABLE_BLENDS_COMP_WIDTHS
from ..constants import TABLE_IMPORTS_EXPORTS_HEADER
from ..constants import TABLE_IMPORTS_EXPORTS_HEADER_STYLE
from ..constants import TABLE_IMPORTS_EXPORTS_BL_WIDTHS
from ..constants import TABLE_IMPORTS_EXPORTS_SUBS_WIDTHS
from ..constants import TABLE_ROW_EMPTY_STYLE_IMP_EXP
from ..constants import TABLE_ROW_EMPTY_IMP_EXP

from ..util import mk_table_blends
from ..util import mk_table_substances
from ..util import page_title_section
from ..util import table_from_data
from ..util import STYLES
from ..util import TABLE_STYLES

from .imp_exp_helper import big_table_row
from .imp_exp_helper import component_row

from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph

from django.utils.translation import gettext_lazy as _


def export_imports(submission):
    grouping = submission.article7imports

    table_substances = tuple(mk_table_substances(grouping, big_table_row))
    table_blends = tuple(mk_table_blends(
        grouping, big_table_row, component_row, TABLE_BLENDS_COMP_HEADER,
        TABLE_BLENDS_COMP_STYLE, TABLE_BLENDS_COMP_WIDTHS
    ))

    style = lambda data: (
        TABLE_IMPORTS_EXPORTS_HEADER_STYLE + TABLE_STYLES + (
            () if data else TABLE_ROW_EMPTY_STYLE_IMP_EXP
        )
    )

    subst_table = table_from_data(
        data=table_substances, isBlend=False,
        header=TABLE_IMPORTS_EXPORTS_HEADER(False, 'import'),
        colWidths=TABLE_IMPORTS_EXPORTS_SUBS_WIDTHS,
        style=style(table_substances),
        repeatRows=2, emptyData=TABLE_ROW_EMPTY_IMP_EXP
    )

    blends_table = table_from_data(
        data=table_blends, isBlend=True,
        header=TABLE_IMPORTS_EXPORTS_HEADER(True, 'import'),
        colWidths=TABLE_IMPORTS_EXPORTS_BL_WIDTHS,
        style=style(table_blends),
        repeatRows=2, emptyData=TABLE_ROW_EMPTY_IMP_EXP
    )

    imports_page = (
        Paragraph(_('1.1 Substances'), STYLES['Heading2']),
        subst_table,
        PageBreak(),
        Paragraph(_('1.2 Blends'), STYLES['Heading2']),
        blends_table,
        PageBreak(),
    )

    return page_title_section(
        title=_('IMPORTS'),
        explanatory= _(
            'Annexes A, B, C and E substances in metric tonnes (not ODP tonnes)'
        )
    ) + imports_page
