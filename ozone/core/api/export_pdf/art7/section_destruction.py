from django.utils.translation import gettext_lazy as _

from .constants import TABLE_DEST_HEADER
from .constants import TABLE_DEST_HEADER_STYLE
from .constants import TABLE_DEST_COMP_HEADER
from .constants import TABLE_DEST_COMP_WIDTH
from .constants import TABLE_DEST_WIDTH
from .constants import TABLE_BLENDS_COMP_STYLE

from ..util import get_big_float
from ..util import get_comments_section
from ..util import mk_table_blends
from ..util import mk_table_substances
from ..util import p_c, p_r
from ..util import page_title_section
from ..util import table_from_data
from ..util import to_precision
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
    percent = component.percentage

    return (
        p_c(_(component.substance.name)),
        p_r('<b>{}%</b>'.format(round(percent * 100, 1))),
        p_r(to_precision(blend.quantity_destroyed * percent, 3))
    )


def export_destruction(submission):
    data = submission.article7destructions

    table_substances = tuple(mk_table_substances(data, big_table_row))
    table_blends = tuple(mk_table_blends(
        data, big_table_row, component_row, TABLE_DEST_COMP_HEADER,
        TABLE_BLENDS_COMP_STYLE, TABLE_DEST_COMP_WIDTH
    ))

    subst_table = table_from_data(
        data=table_substances, isBlend=False,
        header=TABLE_DEST_HEADER(False),
        colWidths=TABLE_DEST_WIDTH,
        style=TABLE_DEST_HEADER_STYLE + TABLE_STYLES,
        repeatRows=1, emptyData=_('No controlled substances destroyed.')
    )

    blends_table = table_from_data(
        data=table_blends, isBlend=True,
        header=TABLE_DEST_HEADER(True),
        colWidths=TABLE_DEST_WIDTH,
        style=TABLE_DEST_HEADER_STYLE + TABLE_STYLES,
        repeatRows=1, emptyData=_('No blends destroyed.')
    )

    return (
        page_title_section(
            title="%s (%s)" % (_('Destroyed'), _('metric tonnes')),
        ) + (subst_table, blends_table) +
        get_comments_section(submission, 'destruction')
    )
