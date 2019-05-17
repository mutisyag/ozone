from django.utils.translation import gettext_lazy as _
from reportlab.platypus import Paragraph
from reportlab.lib import colors

from ..util import get_big_float
from ..util import get_quantity, get_decision
from ..util import get_comments_section
from ..util import get_remarks
from ..util import rows_to_table
from ..util import p_c, p_l, p_r
from ..util import h2_style
from ..util import col_widths
from ..util import TABLE_STYLES
from ..util import EXEMPTED_FIELDS


def to_row(obj, row_index):
    # row_index represents the current number of table rows, including header
    rows = list()
    styles = list()
    # there are no blends in production form, so it's safe to assume a substance

    # Check if there are any non-null exemption fields
    field_names = [f for f in EXEMPTED_FIELDS if getattr(obj, 'quantity_' + f)]
    first_field = field_names.pop(0) if field_names else None

    # Add base row
    rows.append((
        p_l(obj.substance.group.group_id),
        p_l(obj.substance.name),
        p_r(get_big_float(obj.quantity_total_produced)),
        p_r(get_big_float(obj.quantity_feedstock)),
        p_r(get_big_float(obj.quantity_for_destruction)),
        p_r(get_big_float(get_quantity(obj, first_field))) if first_field else '',
        p_l(
            '%s %s' % (
                EXEMPTED_FIELDS[first_field],
                get_decision(obj, first_field)
            )
        ) if first_field else '',
        p_r(get_big_float(obj.quantity_article_5)),
        p_l(get_remarks(obj)),
    ))

    # Add more rows if there are still fields in field_names
    for f in field_names:
        rows.append((
            # Don't repeat previously shown fields
            '', '', '', '', '',
            p_r(get_big_float(get_quantity(obj, f))),
            p_l('%s %s' % (EXEMPTED_FIELDS[f], get_decision(obj, f))),
            '', '',
        ))

    # quantity_quarantine_pre_shipment
    if obj.quantity_quarantine_pre_shipment:
        # Add two rows for QPS
        rows.extend([
            (
                '', '', '', '', '',
                p_c(_('Amount produced for QPS applications within your country and for export')),
                '', '', '',
            ),
            (
                '', '', '', '', '',
                p_r(get_big_float(obj.quantity_quarantine_pre_shipment)),
                get_decision(obj, 'quarantine_pre_shipment'),
                '', '',
            )
        ])
        current_row = row_index + len(rows) - 1
        styles.extend([
            ('SPAN', (5, current_row-1), (6, current_row-1)),  # Quantity + Decision (heading)
            ('BACKGROUND', (5, current_row-1), (6, current_row-1), colors.lightgrey),
            ('ALIGN', (5, current_row-1), (6, current_row-1), 'CENTER'),
        ])

    if len(rows) > 1:
        current_row = row_index + len(rows) - 1
        styles.extend([
            #  Vertical span of common columns for all exempted rows
            ('SPAN', (0, row_index), (0, current_row)),  # Annex Group
            ('SPAN', (1, row_index), (1, current_row)),  # Substance
            ('SPAN', (2, row_index), (2, current_row)),  # Total production
            ('SPAN', (3, row_index), (3, current_row)),  # Feedstock
            ('SPAN', (4, row_index), (4, current_row)),  # Captured for destruction
            ('SPAN', (7, row_index), (7, current_row)),  # Art 5
            ('SPAN', (8, row_index), (8, current_row)),  # Remarks
        ])
    return (rows, styles)


def export_production(submission):
    data = submission.article7productions.all()
    comments = get_comments_section(submission, 'production')

    if not data and not any(comments):
        return tuple()

    subtitle = Paragraph(
        "%s (%s)" % (_('Production'), _('metric tonnes')),
        h2_style
    )

    styles = list(TABLE_STYLES) + [
         ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
         ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
         ('SPAN', (0, 0), (0, 1)),  # Annex/Group
         ('SPAN', (1, 0), (1, 1)),  # Substance
         ('SPAN', (2, 0), (2, 1)),  # Total production
         ('SPAN', (3, 0), (3, 1)),  # Feedstock
         ('SPAN', (5, 0), (6, 0)),  # Exempted
         ('SPAN', (7, 0), (7, 1)),  # Art 5
         ('SPAN', (8, 0), (8, 1)),  # Remarks
    ]
    header_f1 = [
        (
            p_c(_('Annex/Group')),
            p_c(_('Substance')),
            p_c(_('Total production for all uses')),
            p_c(_('Production for feedstock uses within your country')),
            '',  # Destruction column is not needed for F/I but
                 # it's added (invisible) to have a single to_row function
            p_c(_('Production for exempted essential, '
                  'critical or other uses within your country')),
            '',
            p_c(_('Production for supply to Article 5 countries')),
            p_c(_('Remarks')),
        ),
        (
            '',
            '',
            '',
            '',
            '',
            p_c(_('Quantity')),
            p_c(_('Decision / type of use')),
            '',
            '',
        ),
    ]

    captured_items = list()
    rows = list()

    def prepare_item(obj, num_header_rows):
        (p_rows, p_styles) = to_row(
            p,
            len(rows) + num_header_rows
        )
        rows.extend(p_rows)
        styles.extend(p_styles)

    for p in data:
        if p.substance.is_captured:
            # process them in a second pass
            captured_items.append(p)
            continue
        prepare_item(p, len(header_f1))

    table_f1 = rows_to_table(
        header_f1,
        rows,
        col_widths([1.3, 3.5, 2.5, 6, 0, 3, 4.8, 3, 3.5]),
        styles
    )

    # Start over another table, for captured substances
    header_f2 = [
        (
            # Table header for F/II substances
            '', '',
            p_c(_('Captured for all uses')),
            p_c(_('Captured for feedstock uses within your country')),
            p_c(_('Captured for destruction')),
            '', '', '', ''
        ),
    ]
    styles = list(TABLE_STYLES) + [
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
    ]
    rows = list()
    for p in captured_items:
        prepare_item(p, len(header_f2))

    table_f2 = rows_to_table(
        header_f2,
        rows,
        col_widths([1.3, 3.5, 2.5, 3, 3, 3, 4.8, 3, 3.5]),
        styles
    )

    return (subtitle, table_f1, table_f2) + comments
