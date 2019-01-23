from django.utils.translation import gettext_lazy as _
from reportlab.platypus import Paragraph
from reportlab.platypus import PageBreak

from .constants import TABLE_DEST_HEADER
from .constants import TABLE_DEST_HEADER_STYLE
from .constants import TABLE_DEST_COMP_HEADER
from .constants import TABLE_DEST_COMP_WIDTH
from .constants import TABLE_DEST_WIDTH
from .constants import TABLE_ROW_EMPTY_DEST
from .constants import TABLE_ROW_EMPTY_STYLE_DEST
from .constants import TABLE_BLENDS_COMP_STYLE

from ..util import get_big_float
from ..util import get_comments_section
from ..util import mk_table_blends
from ..util import mk_table_substances
from ..util import p_c
from ..util import page_title_section
from ..util import table_from_data
from ..util import to_precision
from ..util import STYLES
from ..util import TABLE_STYLES


def big_table_row(obj, isBlend):
    col_1 = obj.blend.type if isBlend else obj.substance.group.group_id
    col_2 = obj.blend.blend_id if isBlend else obj.substance.name

    return (
        p_c(_(col_1)),
        p_c(_(col_2)),
        p_c(get_big_float(obj.quantity_destroyed or '')),
        p_c(_(obj.remarks_party or '')),
        p_c(_(obj.remarks_os or '')),
    )

def component_row(component, blend):
    ptg = component.percentage

    return (
        p_c(_(component.substance)),
        p_c('<b>{}%</b>'.format(round(ptg * 100, 1))),
        p_c(to_precision(blend.quantity_destroyed * ptg, 3))
    )

def export_destruction(submission):
    grouping = submission.article7destructions

    comments_section = get_comments_section(submission, 'destruction')

    table_substances = tuple(mk_table_substances(grouping, big_table_row))
    table_blends = tuple(mk_table_blends(
        grouping, big_table_row, component_row, TABLE_DEST_COMP_HEADER,
        TABLE_BLENDS_COMP_STYLE, TABLE_DEST_COMP_WIDTH
    ))

    style = lambda data: (
        TABLE_DEST_HEADER_STYLE + TABLE_STYLES + (
            () if data else TABLE_ROW_EMPTY_STYLE_DEST
        )
    )

    subst_table = table_from_data(
        data=table_substances, isBlend=False,
        header=TABLE_DEST_HEADER(False),
        colWidths=TABLE_DEST_WIDTH,
        style=style(table_substances),
        repeatRows=1, emptyData=TABLE_ROW_EMPTY_DEST
    )

    blends_table = table_from_data(
        data=table_blends, isBlend=True,
        header=TABLE_DEST_HEADER(True),
        colWidths=TABLE_DEST_WIDTH,
        style=style(table_blends),
        repeatRows=1, emptyData=TABLE_ROW_EMPTY_DEST
    )

    destr_page = (
        Paragraph(_('4.1 Substances'), STYLES['Heading2']),
        subst_table,
        PageBreak(),
        Paragraph(_('4.2 Blends'), STYLES['Heading2']),
        blends_table,
        PageBreak(),
        Paragraph(_('4.3 Comments'), STYLES['Heading2'])
    )

    return page_title_section(
        title=_('QUANTITY OF SUBSTANCES DESTROYED '),
        explanatory=_(
            'in tonnes (not ODP or GWP tonnes) Annex A, B, C, E and F substances'
        )
    ) + destr_page + comments_section
