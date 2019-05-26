from django.utils.translation import gettext_lazy as _
from reportlab.lib import colors
from reportlab.platypus import Paragraph

from ..util import (
    col_widths,
    sum_decimals,
    exclude_blend_items,
    get_big_float,
    get_comments_section,
    get_quantity,
    get_decision,
    get_remarks,
    get_substance_or_blend_name,
    get_group_name,
    h2_style,
    p_c, p_l, p_r,
    rows_to_table,
    TABLE_STYLES,
    EXEMPTED_FIELDS
)


def to_row(obj, row_index, party_field, text_qps):
    # row_index represents the current number of table rows, including header
    rows = list()
    styles = list()
    # there are no blends in production form, so it's safe to assume a substance

    # Check if there are any non-null exemption fields
    field_names = [f for f in EXEMPTED_FIELDS if getattr(obj, 'quantity_' + f)]
    first_field = field_names.pop(0) if field_names else None
    party = getattr(obj, party_field)

    # Add base row
    base_row = [
        p_c(get_group_name(obj)),
        p_l(get_substance_or_blend_name(obj)),
        p_l(party.name if party else ''),
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
    ]
    is_subtotal = hasattr(obj, 'is_subtotal')
    rows.append(base_row)
    if is_subtotal:
        base_row[0] = p_r(
            '<b>%s %s</b> (%s)' % (_('Subtotal'), obj.substance.name, _('excluding polyols'))
            if obj.quantity_polyols
            else '<b>%s %s</b>' % (_('Subtotal'), obj.substance.name)
        )
        base_row[1] = ''  # Substance name
        current_row = row_index + len(rows) - 1
        styles.extend([
            ('SPAN', (0, current_row), (2, current_row)),
        ])

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
        # Add two more rows for QPS
        rows.extend([
            (
                '', '', '', '', '', '',
                p_c(text_qps),
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
        # Merge heading with previous row (exempted amounts and decision) when empty
        if not any((first_field, field_names)):
            base_row[6] = p_c(text_qps)
            styles.extend([
                ('SPAN', (6, current_row-2), (7, current_row-1)),  # Quantity
                ('BACKGROUND', (6, current_row-2), (7, current_row-1), colors.lightgrey),
                ('ALIGN', (6, current_row-2), (7, current_row-2), 'CENTER'),
            ])
        else:
            styles.extend([
                ('SPAN', (6, current_row-1), (7, current_row-1)),  # Quantity + Decision (heading)
                ('BACKGROUND', (6, current_row-1), (7, current_row-1), colors.lightgrey),
                ('ALIGN', (6, current_row-1), (7, current_row-1), 'CENTER'),
            ])

    if len(rows) > 1:
        current_row = row_index + len(rows) - 1
        if is_subtotal:
            styles.extend([
                #  Vertical span of common columns for all exempted rows
                ('SPAN', (0, row_index), (2, current_row)),  # Annex Group + Substance + Party
                ('SPAN', (3, row_index), (3, current_row)),  # New amount
                ('SPAN', (4, row_index), (4, current_row)),  # Recovered amount
                ('SPAN', (5, row_index), (5, current_row)),  # Feedstock
                ('SPAN', (8, row_index), (8, current_row)),  # Remarks
            ])
        else:
            styles.extend([
                #  Vertical span of common columns for all exempted rows
                ('SPAN', (0, row_index), (0, current_row)),  # Annex Group
                ('SPAN', (1, row_index), (1, current_row)),  # Substance
                ('SPAN', (2, row_index), (2, current_row)),  # Party
                ('SPAN', (3, row_index), (3, current_row)),  # New amount
                ('SPAN', (4, row_index), (4, current_row)),  # Recovered amount
                ('SPAN', (5, row_index), (5, current_row)),  # Feedstock
                ('SPAN', (8, row_index), (8, current_row)),  # Remarks
            ])
    # quantity_polyols
    if obj.quantity_polyols:
        # Add another row for polyols
        if is_subtotal:
            rows.extend([
                (
                    p_r('<b>%s %s</b>' % (_('Subtotal polyols containing'), obj.substance.name)),
                    '', '', '', '', '',
                    p_r(get_big_float(obj.quantity_polyols)),
                    '', '',
                )
            ])
        else:
            rows.extend([
                (
                    p_r('%s %s' % (_('Polyols containing'), obj.substance.name)),
                    '',
                    p_l(party.name if party else ''),
                    '', '', '',
                    p_r(get_big_float(obj.quantity_polyols)),
                    get_decision(obj, 'polyols'),
                    '',
                )
            ])
        current_row = row_index + len(rows) - 1
        styles.extend([
            #  Vertical span of common columns
            ('SPAN', (8, row_index), (8, current_row)),  # Remarks
            ('SPAN', (0, current_row), (5, current_row)),
        ])
    return (rows, styles)


def merge(items):
    if len(items) <= 1:
        return None
    sub_item = items[0].__class__()
    sub_item.substance = items[0].substance
    sub_item.is_subtotal = True
    for x in items:
        for f in x.QUANTITY_FIELDS + ['quantity_polyols']:
            setattr(sub_item, f, sum_decimals(
                getattr(sub_item, f),
                getattr(x, f)
            ))
    return sub_item


def preprocess_subtotals(data):
    newdata = list()
    substance = None
    subtotal_items = list()
    for item in data:
        # Add subtotal rows when multiple items for the same substance
        # assuming the list of items is pre-sorted by substance
        if substance and item.substance_id != substance.pk:
            # substance has changed
            sub_item = merge(subtotal_items)
            if sub_item:
                newdata.append(sub_item)
            subtotal_items = list()
            substance = item.substance
        newdata.append(item)
        subtotal_items.append(item)
        if not substance:
            # First item
            substance = item.substance
    # Process last set of items
    sub_item = merge(subtotal_items)
    if sub_item:
        newdata.append(sub_item)
    return newdata


def _export(data, comments, party_field, texts):
    if not data and not any(comments):
        return tuple()

    subtitle = Paragraph(texts['section_title'], h2_style)

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
            p_c(texts['party']),
            p_c(texts['total_quantity']),
            '',
            p_c(texts['feedstock_quantity']),
            p_c(texts['exempted_quantity']),
            '',
            p_c(_('Remarks')),
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
            '',
        ),
    ]

    data = preprocess_subtotals(data)

    rows = list()
    for item in data:
        (_rows, _styles) = to_row(
            item,
            len(rows) + len(header),
            party_field,
            texts['qps_quantity']
        )
        rows.extend(_rows)
        styles.extend(_styles)

    table = rows_to_table(
        header,
        rows,
        col_widths([1.3, 2.5, 3.5, 2.5, 2.5, 2.5, 2.5, 5, 5]),
        styles
    )

    return (subtitle, table) + comments


def export_imports(submission):
    data = exclude_blend_items(submission.article7imports)
    comments = get_comments_section(submission, 'imports')
    texts = {
        'section_title': "%s (%s)" % (_('Imports'), _('metric tonnes')),
        'party': _('Exporting country/region/territory'),
        'total_quantity': _('Total quantity imported for all uses'),
        'exempted_quantity': _('Quantity of new substance imported for exempted essential,'
                               'critical, high-ambient-temperature or other uses'),
        'feedstock_quantity': _('Import for feedstock'),
        'qps_quantity': _('Amount imported for QPS applications within your country'),
    }
    return _export(data, comments, 'source_party', texts)


def export_exports(submission):
    data = exclude_blend_items(submission.article7exports)
    comments = get_comments_section(submission, 'exports')
    texts = {
        'section_title': "%s (%s)" % (_('Exports'), _('metric tonnes')),
        'party': _('Importing country/region/territory'),
        'total_quantity': _('Total quantity exported for all uses'),
        'exempted_quantity': _('Quantity of new substance exported for exempted essential,'
                               'critical, high-ambient-temperature or other uses'),
        'feedstock_quantity': _('Export for feedstock'),
        'qps_quantity': _('Amount exported for QPS applications'),
    }
    return _export(data, comments, 'destination_party', texts)
