from django.utils.translation import gettext_lazy as _
from reportlab.platypus import Paragraph
from reportlab.lib import colors

from ..util import get_big_float
from ..util import get_comments_section
from ..util import exclude_blend_items
from ..util import get_substance_or_blend_name
from ..util import rows_to_table
from ..util import get_remarks
from ..util import p_c, p_r, p_l
from ..util import h2_style
from ..util import TABLE_STYLES
from ..util import col_widths


def table_row(obj):
    return (
        p_c(obj.substance.group.name if obj.substance else ''),
        p_l(get_substance_or_blend_name(obj)),
        p_r(get_big_float(obj.quantity_destroyed)),
        p_l(get_remarks(obj)),
    )


def export_destruction(submission):

    subtitle = Paragraph(
        "%s (%s)" % (_('Destroyed'), _('metric tonnes')),
        h2_style
    )

    data = exclude_blend_items(submission.article7destructions)
    comments = get_comments_section(submission, 'destruction')

    if not data and not any(comments):
        return tuple()

    table_header = ((
        p_c(_('Annex/Group')),
        p_c(_('Substance or mixture')),
        p_c(_('Quantity destroyed')),
        p_c(_('Remarks')),
    ),)

    table_style = TABLE_STYLES + (
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
    )

    table = rows_to_table(
        table_header,
        tuple(map(table_row, data)),
        col_widths([3, 6, 4, 12]),
        table_style
    )

    return (subtitle, table) + comments
