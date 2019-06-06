from django.utils.translation import gettext_lazy as _
from reportlab.platypus import Paragraph

from ..util import get_big_float
from ..util import get_comments_section

from ..util import (
    exclude_blend_items,
    get_group_name,
    get_substance_or_blend_name,
    rows_to_table,
    get_remarks,
    sm_c, sm_r, sm_l,
    h2_style,
    DOUBLE_HEADER_TABLE_STYLES,
    col_widths,
)


def table_row(obj):
    return (
        sm_c(get_group_name(obj)),
        sm_l(get_substance_or_blend_name(obj)),
        sm_l(obj.trade_party.name if obj.trade_party else ''),
        sm_r(get_big_float(obj.quantity_import_new)),
        sm_r(get_big_float(obj.quantity_import_recovered)),
        sm_r(get_big_float(obj.quantity_export_new)),
        sm_r(get_big_float(obj.quantity_export_recovered)),
        sm_l(get_remarks(obj)),
    )


def export_nonparty(submission):
    data = exclude_blend_items(submission.article7nonpartytrades)
    comments = get_comments_section(submission, 'nonparty')

    if not data and not any(comments):
        return tuple()

    subtitle = Paragraph(
        _("Imports from and/or exports to non-parties"),
        h2_style
    )

    table_header = (
        (
            sm_c(_('Annex/Group')),
            sm_c(_('Substance or mixture')),
            sm_c(_('Exporting or destination country/region/territory')),
            sm_c(_('Quantity of imports from non-parties')),
            '',
            sm_c(_('Quantity of exports from non-parties')),
            '',
            sm_c(_('Remarks')),
        ),
        (
            '',
            '',
            '',
            sm_c(_('New imports')),
            sm_c(_('Recovered and reclaimed imports')),
            sm_c(_('New exports')),
            sm_c(_('Recovered and reclaimed exports')),
            '',
        )
    )

    table_style = DOUBLE_HEADER_TABLE_STYLES + (
        ('SPAN', (0, 0), (0, 1)),  # Annex group
        ('SPAN', (1, 0), (1, 1)),  # Substance
        ('SPAN', (2, 0), (2, 1)),  # Party
        ('SPAN', (3, 0), (4, 0)),  # Imports
        ('SPAN', (5, 0), (6, 0)),  # Exports
        ('SPAN', (7, 0), (7, 1)),  # Remarks
    )

    table = rows_to_table(
        table_header,
        tuple(map(table_row, data)),
        col_widths([2.1, 5, 4, 2.3, 2.6, 2.3, 2.6, 6.4]),
        table_style
    )

    return (subtitle, table) + comments
