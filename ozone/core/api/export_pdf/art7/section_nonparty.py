from django.utils.translation import gettext_lazy as _
from reportlab.platypus import Paragraph
from reportlab.lib import colors

from ..util import get_big_float
from ..util import get_comments_section
from ..util import to_precision

from ..util import exclude_blend_items
from ..util import get_group_name
from ..util import get_substance_or_blend_name
from ..util import rows_to_table
from ..util import get_remarks
from ..util import p_c, p_r, p_l
from ..util import h2_style
from ..util import TABLE_STYLES
from ..util import col_widths


def table_row(obj):
    return (
        p_c(get_group_name(obj)),
        p_l(get_substance_or_blend_name(obj)),
        p_l(obj.trade_party.name if obj.trade_party else ''),
        p_r(get_big_float(obj.quantity_import_new)),
        p_r(get_big_float(obj.quantity_import_recovered)),
        p_r(get_big_float(obj.quantity_export_new)),
        p_r(get_big_float(obj.quantity_export_recovered)),
        p_l(get_remarks(obj)),
    )


def component_row(component, blend):
    ptg = component.percentage

    return (
        component.substance,
        p_c('<b>{}%</b>'.format(round(ptg * 100, 1))),
        to_precision(blend.quantity_import_new * ptg, 3),
        to_precision(blend.quantity_import_recovered * ptg, 3),
        to_precision(blend.quantity_export_new * ptg, 3),
        to_precision(blend.quantity_export_recovered * ptg, 3),
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
            p_c(_('Annex/Group')),
            p_c(_('Substance or mixture')),
            p_c(_('Exporting or destination country/region/territory')),
            p_c(_('Quantity of imports from non-parties')),
            '',
            p_c(_('Quantity of exports from non-parties')),
            '',
            p_c(_('Remarks')),
        ),
        (
            '',
            '',
            '',
            p_c(_('New imports')),
            p_c(_('Recovered and reclaimed imports')),
            p_c(_('New exports')),
            p_c(_('Recovered and reclaimed exports')),
            '',
        )
    )

    table_style = TABLE_STYLES + (
        ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
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
        col_widths([2.1, 5, 4, 2.3, 2.7, 2.3, 2.7, 6.5]),
        table_style
    )

    return (subtitle, table) + comments
