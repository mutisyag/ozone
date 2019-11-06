from django.utils.translation import gettext_lazy as _
from reportlab.platypus import Paragraph

from ozone.core.models.utils import sum_decimals

from ..util import (
    col_widths,
    format_decimal,
    get_comments_section,
    get_quantity,
    get_decision,
    get_remarks,
    get_substance_or_blend_name,
    get_group_name,
    h2_style,
    sm_c, sm_l, sm_r,
    smb_l, smb_r,
    rows_to_table,
    grid_color,
    lighter_grey,
    DOUBLE_HEADER_TABLE_STYLES,
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
    substance_name = get_substance_or_blend_name(obj)
    is_subtotal = hasattr(obj, 'is_subtotal')
    p_r_func = smb_r if is_subtotal else sm_r
    base_row = [
        sm_c(get_group_name(obj)),
        sm_l(substance_name),
        sm_l(party.name if party else ''),
        p_r_func(format_decimal(obj.quantity_total_new)),
        p_r_func(format_decimal(obj.quantity_total_recovered)),
        p_r_func(format_decimal(obj.quantity_feedstock)),
        p_r_func(format_decimal(get_quantity(obj, first_field)) if first_field else ''),
        sm_l(
            '%s %s' % (
                EXEMPTED_FIELDS[first_field],
                get_decision(obj, first_field)
            )
        ) if first_field else '',
        sm_l(get_remarks(obj)),
    ]
    rows.append(base_row)
    if obj.blend:
        current_row = row_index + len(rows) - 1
        # Move blend name to first column and merge with second column
        base_row[0] = base_row[1]
        styles.extend([
            ('SPAN', (0, current_row), (1, current_row)),
        ])
    if is_subtotal:
        base_row[0] = smb_l(
            '%s %s (%s)' % (_('Subtotal'), substance_name, _('excluding polyols'))
            if obj.quantity_polyols
            else '%s %s' % (_('Subtotal'), substance_name)
        )
        base_row[1] = ''  # Substance name
        current_row = row_index + len(rows) - 1
        styles.extend([
            ('SPAN', (0, current_row), (2, current_row)),
            ('LINEABOVE', (0, current_row), (-1, current_row), 0.5, grid_color),
        ])

    # Add more rows if there are still fields in field_names
    for f in field_names:
        rows.append((
            # Don't repeat previously shown fields
            '', '', '', '', '', '',
            p_r_func(format_decimal(get_quantity(obj, f))),
            sm_l('%s %s' % (EXEMPTED_FIELDS[f], get_decision(obj, f))),
            '',
        ))

    # quantity_quarantine_pre_shipment
    if obj.quantity_quarantine_pre_shipment:
        # Add two more rows for QPS
        rows.extend([
            (
                '', '', '', '', '', '',
                sm_c(text_qps),
                '', '',
            ),
            (
                '', '', '', '', '', '',
                p_r_func(format_decimal(obj.quantity_quarantine_pre_shipment)),
                sm_l(get_decision(obj, 'quarantine_pre_shipment')),
                '',
            )
        ])
        current_row = row_index + len(rows) - 1
        # Merge heading with previous row (exempted amounts and decision) when empty
        if not any((first_field, field_names)):
            base_row[6] = sm_c(text_qps)
            styles.extend([
                ('SPAN', (6, current_row-2), (7, current_row-1)),  # Quantity
                ('BACKGROUND', (6, current_row-2), (7, current_row-1), lighter_grey),
                ('ALIGN', (6, current_row-2), (7, current_row-2), 'CENTER'),
            ])
        else:
            styles.extend([
                ('SPAN', (6, current_row-1), (7, current_row-1)),  # Quantity + Decision (heading)
                ('BACKGROUND', (6, current_row-1), (7, current_row-1), lighter_grey),
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
        current_row = row_index + len(rows)
        if is_subtotal:
            rows.extend([
                (
                    smb_l('%s %s' % (_('Subtotal polyols containing'), obj.substance.name)),
                    '', '', '', '', '',
                    smb_r(format_decimal(obj.quantity_polyols)),
                    '', '',
                )
            ])
            styles.extend([
                #  Vertical span of common columns
                ('SPAN', (8, row_index), (8, current_row)),  # Remarks
                ('SPAN', (0, current_row), (2, current_row)),
            ])
        else:
            rows.extend([
                (
                    sm_r('%s %s' % (_('Polyols containing'), obj.substance.name)),
                    '',
                    sm_l(party.name if party else ''),
                    '', '', '',
                    sm_r(format_decimal(obj.quantity_polyols)),
                    sm_l(get_decision(obj, 'polyols')),
                    '',
                )
            ])
            styles.extend([
                #  Vertical span of common columns
                ('SPAN', (8, row_index), (8, current_row)),  # Remarks
                ('SPAN', (0, current_row), (1, current_row)),
            ])
    return (rows, styles)


def merge(items):
    if len(items) <= 1:
        return None
    sub_item = items[0].__class__()
    sub_item.substance = items[0].substance
    sub_item.blend = items[0].blend
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
    substance = None  # substance or blend
    subtotal_items = list()
    for item in data:
        # Add subtotal rows when multiple items for the same substance
        # assuming the list of items is pre-sorted by substance
        if substance and item.substance_id != substance.pk and item.blend_id != substance.pk:
            # substance has changed
            sub_item = merge(subtotal_items)
            if sub_item:
                newdata.append(sub_item)
            subtotal_items = list()
            substance = item.substance or item.blend
        newdata.append(item)
        subtotal_items.append(item)
        if not substance:
            # First item
            substance = item.substance or item.blend
    # Process last set of items
    sub_item = merge(subtotal_items)
    if sub_item:
        newdata.append(sub_item)
    return newdata


def _export(data, comments, party_field, texts):
    if not data and not any(comments):
        return tuple()

    subtitle = Paragraph(texts['section_title'], h2_style)

    styles = list(DOUBLE_HEADER_TABLE_STYLES) + [
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
            sm_c(_('Annex/Group')),
            sm_c(_('Substance')),
            sm_c(texts['party']),
            sm_c(texts['total_quantity']),
            '',
            sm_c(texts['feedstock_quantity']),
            sm_c(texts['exempted_quantity']),
            '',
            sm_c(_('Remarks')),
        ),
        (
            '',
            '',
            '',
            sm_c(_('New')),
            sm_c(_('Recovered')),
            '',
            sm_c(_('Quantity')),
            sm_c(_('Decision / type of use or remark')),
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
        col_widths([1.0, 4, 2.9, 2.5, 2.5, 2.5, 2.5, 4.8, 4.8]),
        styles
    )

    return (subtitle, table) + comments


def export_imports(submission, queryset):
    comments = get_comments_section(submission, 'imports')
    texts = {
        'section_title': "%s (%s)" % (_('Imports'), _('metric tonnes')),
        'party': _('Exporting country/region/territory'),
        'total_quantity': _('Total quantity imported for all uses'),
        'exempted_quantity': _('Quantity of new substance imported for exempted essential, '
                               'critical, high-ambient-temperature or other uses'),
        'feedstock_quantity': _('Import for feedstock'),
        'qps_quantity': _('Amount imported for QPS applications within your country'),
    }
    return _export(list(queryset), comments, 'source_party', texts)


def export_exports(submission, queryset):
    comments = get_comments_section(submission, 'exports')
    texts = {
        'section_title': "%s (%s)" % (_('Exports'), _('metric tonnes')),
        'party': _('Importing country/region/territory'),
        'total_quantity': _('Total quantity exported for all uses'),
        'exempted_quantity': _('Quantity of new substance exported for exempted essential, '
                               'critical, high-ambient-temperature or other uses'),
        'feedstock_quantity': _('Export for feedstock'),
        'qps_quantity': _('Amount exported for QPS applications'),
    }
    return _export(list(queryset), comments, 'destination_party', texts)
