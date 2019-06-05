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
    p_c,
    p_r,
    p_l,
    h2_style,
    SINGLE_HEADER_TABLE_STYLES,
    col_widths,
)


def table_row(obj):
    return (
        p_c(get_group_name(obj)),
        p_l(get_substance_or_blend_name(obj)),
        p_r(get_big_float(obj.quantity_destroyed)),
        p_l(get_remarks(obj)),
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
        p_c(_('Annex/Group')),
        p_c(_('Substance or mixture')),
        p_c(_('Quantity destroyed')),
        p_c(_('Remarks')),
    ),)

    table = rows_to_table(
        table_header,
        tuple(map(table_row, data)),
        col_widths([2.1, 8, 4, 13.2]),
        SINGLE_HEADER_TABLE_STYLES
    )

    return (subtitle, table) + comments
