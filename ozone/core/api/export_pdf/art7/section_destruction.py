from django.utils.translation import gettext_lazy as _
from reportlab.platypus import Paragraph

from ..util import (
    get_big_float,
    get_comments_section,
    exclude_blend_items,
    get_substance_or_blend_name,
    get_group_name,
    rows_to_table,
    get_remarks,
    sm_c, sm_r, sm_l,
    h2_style,
    SINGLE_HEADER_TABLE_STYLES,
    col_widths,
)


def table_row(obj):
    return (
        sm_c(get_group_name(obj)),
        sm_l(get_substance_or_blend_name(obj)),
        sm_r(get_big_float(obj.quantity_destroyed)),
        sm_l(get_remarks(obj)),
    )


def export_destruction(submission):
    data = exclude_blend_items(submission.article7destructions)
    comments = get_comments_section(submission, 'destruction')

    if not data and not any(comments):
        return tuple()

    subtitle = Paragraph(
        "%s (%s)" % (_('Destroyed'), _('metric tonnes')),
        h2_style
    )

    table_header = ((
        sm_c(_('Annex/Group')),
        sm_c(_('Substance or mixture')),
        sm_c(_('Quantity destroyed')),
        sm_c(_('Remarks')),
    ),)

    table = rows_to_table(
        table_header,
        tuple(map(table_row, data)),
        col_widths([2.1, 8, 4, 13.2]),
        SINGLE_HEADER_TABLE_STYLES
    )

    return (subtitle, table) + comments
