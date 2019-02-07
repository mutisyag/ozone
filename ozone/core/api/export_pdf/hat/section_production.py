from .hat_helper import big_table_row
from .hat_helper import TABLE_IMPORTS_HEADER
from .hat_helper import TABLE_IMPORTS_HEADER_STYLE
from .hat_helper import TABLE_ROW_EMPTY_STYLE_IMP
from .hat_helper import TABLE_ROW_EMPTY_IMP

from ..util import get_comments_section
from ..util import page_title_section
from ..util import table_from_data
from ..util import STYLES
from ..util import TABLE_STYLES

from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph

from django.utils.translation import gettext_lazy as _
from functools import partial


def mk_table_substances(submission):
    objs = submission.highambienttemperatureproductions.all()
    row_fct = partial(big_table_row, isBlend=False)
    return map(row_fct, objs)


def export_production(submission):
    table_substances = tuple(mk_table_substances(submission))

    comments_section = get_comments_section(submission, 'hat_production')

    style = lambda data: (
        TABLE_IMPORTS_HEADER_STYLE + TABLE_STYLES + (
            () if data else TABLE_ROW_EMPTY_STYLE_IMP
        )
    )

    subst_table = table_from_data(
        data=table_substances, isBlend=False,
        header=TABLE_IMPORTS_HEADER(False, 'produc'),
        colWidths=None,
        style=style(table_substances),
        repeatRows=2, emptyData=TABLE_ROW_EMPTY_IMP
    )

    prod_page = (
        Paragraph(_('2.1 Substances'), STYLES['Heading2']),
        subst_table,
        PageBreak(),
        Paragraph(_('2.2 Comments'), STYLES['Heading2']),
    )

    return page_title_section(
        title=_('PRODUCTION'),
        explanatory= _(
            'Annex F substances for exempted subsectors in metric tonnes '
            '(not ODP or CO2-equivalent tonnes)'
        )
    ) + prod_page + comments_section
