from django.utils.translation import gettext_lazy as _
from functools import partial

from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph

from .imp_exp_helper import big_table_row
from .imp_exp_helper import component_row
from .imp_exp_helper import get_header

from ..util import page_title_section
from ..util import table_from_data
from ..util import table_with_blends
from ..util import STYLES
from ..util import TABLE_STYLES

from ..constants import TABLE_BLENDS_COMP_HEADER
from ..constants import TABLE_BLENDS_COMP_STYLE
from ..constants import TABLE_BLENDS_COMP_WIDTHS
from ..constants import TABLE_IMPORTS_EXPORTS_HEADER_STYLE
from ..constants import TABLE_IMPORTS_EXPORTS_BL_WIDTHS
from ..constants import TABLE_IMPORTS_EXPORTS_SUBS_WIDTHS
from ..constants import TABLE_ROW_EMPTY_STYLE_IMP_EXP
from ..constants import TABLE_ROW_EMPTY_IMP_EXP


def mk_table_substances(submission):
    exports = submission.article7exports.exclude(substance=None)
    row = partial(big_table_row, isBlend=False)
    return map(row, exports.filter(blend_item=None))

def mk_table_blends(submission):
    exports = submission.article7exports.filter(substance=None)
    row = partial(big_table_row, isBlend=True)

    blends = map(row, exports)

    return table_with_blends(
        blends=blends,
        grouping=exports,
        make_component=component_row,
        header=TABLE_BLENDS_COMP_HEADER,
        style=TABLE_BLENDS_COMP_STYLE,
        widths=TABLE_BLENDS_COMP_WIDTHS
    )

def export_exports(submission):
    table_substances = tuple(mk_table_substances(submission))
    table_blends = tuple(mk_table_blends(submission))

    style = lambda data: (
        TABLE_IMPORTS_EXPORTS_HEADER_STYLE + TABLE_STYLES + (
        () if data else TABLE_ROW_EMPTY_STYLE_IMP_EXP
    )
    )

    subst_table = table_from_data(
        data=table_substances, isBlend=False,
        header=get_header(isBlend="False", type='export'),
        colWidths=TABLE_IMPORTS_EXPORTS_SUBS_WIDTHS,
        style=style(table_substances),
        repeatRows=2, emptyData=TABLE_ROW_EMPTY_IMP_EXP
    )

    blends_table = table_from_data(
        data=table_blends, isBlend=True,
        header=get_header(isBlend="True", type='export'),
        colWidths=TABLE_IMPORTS_EXPORTS_BL_WIDTHS,
        style=style(table_blends),
        repeatRows=2, emptyData=TABLE_ROW_EMPTY_IMP_EXP
    )

    exports_page = (
        Paragraph(_('2.1 Substances'), STYLES['Heading2']),
        subst_table,
        PageBreak(),
        Paragraph(_('2.2 Blends'), STYLES['Heading2']),
        blends_table,
        PageBreak(),
    )

    return page_title_section(
        title=_('EXPORTS'),
        explanatory=_(
            'Annexes A, B, C and E substances in metric tonnes (not ODP tonnes)'
        )
    ) + exports_page
