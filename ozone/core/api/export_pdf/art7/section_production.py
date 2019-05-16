from django.utils.translation import gettext_lazy as _
from reportlab.platypus import Paragraph
from reportlab.lib import colors

from ..util import get_big_float
from ..util import get_comments_section
from ..util import get_decisions
from ..util import get_preship_or_polyols_q
from ..util import get_quantity_cell
from ..util import get_quantities
from ..util import get_substance_label
from ..util import rows_to_table
from ..util import p_c, p_l, p_r
from ..util import h2_style
from ..util import col_widths
from ..util import TABLE_STYLES


def table_row_f1(obj):
    substance = obj.substance

    quantities = get_quantities(obj)
    extra_q = get_preship_or_polyols_q(obj)
    q_cell = get_quantity_cell(quantities, extra_q)

    decisions = get_decisions(obj)
    d_label = get_substance_label(decisions, type='decision')

    return (
        substance.group.group_id,
        p_l(substance.name),
        p_r(get_big_float(obj.quantity_total_produced)),
        p_r(get_big_float(obj.quantity_feedstock)),
        q_cell,
        (d_label,),
        p_r(get_big_float(obj.quantity_article_5))
    )


def table_row_f2(obj):
    substance = obj.substance

    quantities = get_quantities(obj)
    extra_q = get_preship_or_polyols_q(obj)
    q_cell = get_quantity_cell(quantities, extra_q)

    decisions = get_decisions(obj)
    d_label = get_substance_label(decisions, type='decision')

    return (
        substance.group.group_id,
        p_l(substance.name),
        p_r(get_big_float(obj.quantity_total_produced)),
        p_r(get_big_float(obj.quantity_feedstock)),
        p_r(get_big_float(obj.quantity_for_destruction)),
        q_cell,
        (d_label,),
        p_r(get_big_float(obj.quantity_article_5))
    )


def export_production(submission):
    data = submission.article7productions
    comments = get_comments_section(submission, 'production')

    if not data and not any(comments):
        return tuple()

    subtitle = Paragraph(
        "%s (%s)" % (_('Production'), _('metric tonnes')),
        h2_style
    )

    data_f1 = data.exclude(substance__is_captured=True)
    data_f2 = data.filter(substance__is_captured=True)

    table_f1_header = (
        (
            p_c(_('Annex/Group')),
            p_c(_('Substance')),
            p_c(_('Total production for all uses')),
            p_c(_('Production for feedstock uses within your country')),
            p_c(_('Production for exempted essential, '
                  'critical or other uses within your country')),
            '',
            p_c(_('Production for supply to Article 5 countries')),
        ),
        (
            '',
            '',
            '',
            '',
            p_c(_('Quantity')),
            p_c(_('Decision / type of use')),
            '',
        ),
    )
    table_f1_style = TABLE_STYLES + (
        ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
        ('SPAN', (0, 0), (0, 1)),  # Annex/Group
        ('SPAN', (1, 0), (1, 1)),  # Substance
        ('SPAN', (2, 0), (2, 1)),  # Total production
        ('SPAN', (3, 0), (3, 1)),  # Feedstock
        ('SPAN', (4, 0), (5, 0)),  # Excempted
        ('SPAN', (6, 0), (6, 1)),  # Art 5
    )
    table_f1 = rows_to_table(
        table_f1_header,
        tuple(map(table_row_f1, data_f1)),
        col_widths([1.3, 3.5, 3, 7, 3, 5.8, 4]),
        table_f1_style
    )
    table_f2_header = (
        (
            '',
            '',
            p_c(_('Captured for all uses')),
            p_c(_('Captured for feedstock uses within your country')),
            p_c(_('Captured for destruction')),
            '',
            '',
            '',
        ),
    )
    table_f2_style = TABLE_STYLES + (
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
    )
    table_f2 = rows_to_table(
        table_f2_header,
        tuple(map(table_row_f2, data_f2)),
        col_widths([1.3, 3.5, 3, 4, 3, 3, 5.8, 4]),
        table_f2_style
    )

    return (subtitle, table_f1, table_f2) + comments
