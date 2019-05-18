from django.utils.translation import gettext_lazy as _
from reportlab.lib import colors
from reportlab.platypus import Paragraph

from ..util import col_widths
from ..util import exclude_blend_items
from ..util import get_big_float
from ..util import get_comments_section
from ..util import get_quantity, get_decision
from ..util import get_remarks
from ..util import get_substance_or_blend_name
from ..util import h2_style
from ..util import p_c, p_l, p_r
from ..util import rows_to_table
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
        p_c(obj.substance.group.name if obj.substance else ''),  # Might be a blend
        p_l(get_substance_or_blend_name(obj)),
        p_l(obj.source_party.name if obj.source_party else ''),
        p_r(get_big_float(obj.quantity_total_new)),
        p_r(get_big_float(obj.quantity_total_recovered)),
        p_r(get_big_float(obj.quantity_feedstock)),
        p_r(get_big_float(get_quantity(obj, first_field))) if first_field else '',
        p_l(
            '%s %s' % (
                EXEMPTED_FIELDS[first_field],
                get_decision(obj, first_field)
            )
        ) if first_field else '',
        p_l(get_remarks(obj)),
    ))

    # Add more rows if there are still fields in field_names
    for f in field_names:
        rows.append((
            # Don't repeat previously shown fields
            '', '', '', '', '', '',
            p_r(get_big_float(get_quantity(obj, f))),
            p_l('%s %s' % (EXEMPTED_FIELDS[f], get_decision(obj, f))),
            '',
        ))

    # quantity_quarantine_pre_shipment
    if obj.quantity_quarantine_pre_shipment:
        # Add two rows for QPS
        rows.extend([
            (
                '', '', '', '', '', '',
                p_c(_('Amount imported for QPS applications within your country')),
                '', '',
            ),
            (
                '', '', '', '', '', '',
                p_r(get_big_float(obj.quantity_quarantine_pre_shipment)),
                get_decision(obj, 'quarantine_pre_shipment'),
                '',
            )
        ])
        current_row = row_index + len(rows) - 1
        styles.extend([
            ('SPAN', (6, current_row-1), (7, current_row-1)),  # Quantity + Decision (heading)
            ('BACKGROUND', (6, current_row-1), (7, current_row-1), colors.lightgrey),
            ('ALIGN', (6, current_row-1), (7, current_row-1), 'CENTER'),
        ])

    if len(rows) > 1:
        current_row = row_index + len(rows) - 1
        styles.extend([
            #  Vertical span of common columns for all exempted rows
            ('SPAN', (0, row_index), (0, current_row)),  # Annex Group
            ('SPAN', (1, row_index), (1, current_row)),  # Substance
            ('SPAN', (2, row_index), (2, current_row)),  # Source party
            ('SPAN', (3, row_index), (3, current_row)),  # New amount
            ('SPAN', (4, row_index), (4, current_row)),  # Recovered amount
            ('SPAN', (5, row_index), (5, current_row)),  # Feedstock
            ('SPAN', (8, row_index), (8, current_row)),  # Remarks
        ])
    # quantity_polyols
    if obj.quantity_polyols:
        # Add another row for polyols
        rows.extend([
            (
                '',
                p_l('%s %s' % (_('Polyols containing'), obj.substance.name)),
                p_l(obj.source_party.name if obj.source_party else ''),
                '', '', '',
                p_r(get_big_float(obj.quantity_polyols)),
                get_decision(obj, 'polyols'),
                '',
            )
        ])
        current_row = row_index + len(rows) - 1
    return (rows, styles)


def export_imports(submission):

    data = exclude_blend_items(submission.article7imports)
    comments = get_comments_section(submission, 'imports')
    if not data and not any(comments):
        return tuple()

    subtitle = Paragraph(
        "%s (%s)" % (_('Imports'), _('metric tonnes')),
        h2_style
    )

    styles = list(TABLE_STYLES) + [
         ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
         ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
         ('SPAN', (0, 0), (0, 1)),  # Annex/Group
         ('SPAN', (1, 0), (1, 1)),  # Substance
         ('SPAN', (2, 0), (2, 1)),  # Party
         ('SPAN', (3, 0), (4, 0)),  # Total quantity
         ('SPAN', (5, 0), (5, 1)),  # Feedstock
         ('SPAN', (6, 0), (7, 0)),  # Exempted
         ('SPAN', (8, 0), (8, 1)),  # Remarks
    ]

    header = [
        (
            p_c(_('Annex/Group')),
            p_c(_('Substance')),
            p_c(_('Exporting country/region/territory')),
            p_c(_('Total quantity imported for all uses')),
            '',
            p_c(_('Import for feedstock')),
            p_c(_('Quantity of new substance imported for exempted essential,'
                  'critical, high-ambient-temperature or other uses')),
            ''
        ),
        (
            '',
            '',
            '',
            p_c(_('New')),
            p_c(_('Recovered and reclaimed')),
            '',
            p_c(_('Quantity')),
            p_c(_('Decision / type of use or remark')),
        ),
    ]

    rows = list()
    for item in data:
        (_rows, _styles) = to_row(item, len(rows) + len(header))
        rows.extend(_rows)
        styles.extend(_styles)

    table = rows_to_table(
        header,
        rows,
        col_widths([1.3, 4.3, 3.5, 3, 3, 3, 3, 3.5, 3.5]),
        styles
    )

    return (subtitle, table) + comments
