# from .constants import TABLE_BLENDS_COMP_HEADER
# from .constants import TABLE_BLENDS_COMP_STYLE
# from .constants import TABLE_BLENDS_COMP_WIDTHS
from .hat_helper import TABLE_IMPORTS_HEADER
from .hat_helper import TABLE_IMPORTS_HEADER_STYLE
# from .constants import TABLE_IMPORTS_EXPORTS_BL_WIDTHS
# from .constants import TABLE_IMPORTS_EXPORTS_SUBS_WIDTHS
from .hat_helper import TABLE_ROW_EMPTY_STYLE_IMP
from .hat_helper import TABLE_ROW_EMPTY_IMP

from ..util import get_comments_section
from ..util import mk_table_blends
from ..util import mk_table_substances
from ..util import page_title_section
from ..util import table_from_data
from ..util import STYLES
from ..util import TABLE_STYLES

from .hat_helper import big_table_row

from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph

from django.utils.translation import gettext_lazy as _


def export_imports(submission):
    grouping = submission.highambienttemperatureimports
    # import pdb; pdb.set_trace()

    comments_section = get_comments_section(submission, 'hat_imports')

    table_substances = tuple(mk_table_substances(grouping, big_table_row))
    # table_blends = tuple(mk_table_blends(
    #     grouping, big_table_row, component_row, TABLE_BLENDS_COMP_HEADER,
    #     TABLE_BLENDS_COMP_STYLE, TABLE_BLENDS_COMP_WIDTHS
    # ))

    style = lambda data: (
        TABLE_IMPORTS_HEADER_STYLE + TABLE_STYLES + (
            () if data else TABLE_ROW_EMPTY_STYLE_IMP
        )
    )

    subst_table = table_from_data(
        data=table_substances, isBlend=False,
        header=TABLE_IMPORTS_HEADER(False, 'import'),
        colWidths=None,
        # colWidths=TABLE_IMPORTS_EXPORTS_SUBS_WIDTHS,
        style=style(table_substances),
        repeatRows=2, emptyData=TABLE_ROW_EMPTY_IMP
    )

    # blends_table = table_from_data(
    #     data=table_blends, isBlend=True,
    #     header=TABLE_IMPORTS_EXPORTS_HEADER(True, 'import'),
    #     colWidths=TABLE_IMPORTS_EXPORTS_BL_WIDTHS,
    #     style=style(table_blends),
    #     repeatRows=2, emptyData=TABLE_ROW_EMPTY_IMP_EXP
    # )

    imports_page = (
        Paragraph(_('1.1 Substances'), STYLES['Heading2']),
        subst_table,
        PageBreak(),
        # Paragraph(_('1.2 Blends'), STYLES['Heading2']),
        # blends_table,
        # PageBreak(),
        # Paragraph(_('1.3 Comments'), STYLES['Heading2']),
    )

    return page_title_section(
        title=_('IMPORTS'),
        explanatory= _(
            'Annexes A, B, C and E substances in metric tonnes (not ODP tonnes)'
        )
    ) + imports_page + comments_section
