from django.utils.translation import gettext_lazy as _
from reportlab.platypus import Paragraph

from ..util import (
    get_big_float,
    get_comments_section,
    get_remarks,
    rows_to_table,
    sm_c, sm_l, sm_r,
    h2_style,
    DOUBLE_HEADER_TABLE_STYLES,
    col_widths,
)


def table_row(obj):
    fields = (
        obj.quantity_generated,
        obj.quantity_captured_all_uses,
        obj.quantity_captured_feedstock,
        obj.quantity_captured_for_destruction,
        obj.quantity_feedstock,
        obj.quantity_destroyed,
        obj.quantity_emitted,
    )
    return (
        sm_l(obj.facility_name),
    ) + tuple(
        sm_r(get_big_float(field))
        for field in fields
    ) + (
        sm_l(get_remarks(obj)),
    )


def export_emission(submission):
    data = submission.article7emissions.all()
    comments = get_comments_section(submission, 'emissions')
    if not data and not any(comments):
        return tuple()

    subtitle = Paragraph(
        "%s (%s)" % (_("Emissions of HFC-23"), _("metric tonnes")),
        h2_style
    )

    table_header = (
        (
            sm_c(_('Facility name or identifier')),
            sm_c(_('Total amount generated')),
            sm_c(_('Amount generated and captured')),
            '',
            '',
            sm_c(_('Amount used for feedstock without prior capture')),
            sm_c(_('Amount destroyed without prior capture')),
            sm_c(_('Amount of generated emissions')),
            sm_c(_('Remarks')),
        ),
        (
            '',
            '',
            sm_c(_('For all uses')),
            sm_c(_('For feedstock use in your country')),
            sm_c(_('For destruction')),
            '',
            '',
            '',
            '',
        )
    )
    table_style = DOUBLE_HEADER_TABLE_STYLES + (
        ('SPAN', (0, 0), (0, 1)),  # Facility
        ('SPAN', (1, 0), (1, 1)),  # Total amount
        ('SPAN', (2, 0), (4, 0)),  # Amount generated and captured
        ('SPAN', (5, 0), (5, 1)),  # Feedstock
        ('SPAN', (6, 0), (6, 1)),  # Destroyed
        ('SPAN', (7, 0), (7, 1)),  # Emissions
        ('SPAN', (8, 0), (8, 1)),  # Remarks
    )

    table = rows_to_table(
        table_header,
        tuple(map(table_row, data)),
        col_widths([4, 2.5, 2.4, 2.8, 2.4, 2.6, 2.6, 2.4, 5.6]),
        table_style
    )

    return (subtitle, table) + comments
