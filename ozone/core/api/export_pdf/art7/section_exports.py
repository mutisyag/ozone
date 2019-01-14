from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus import Table
from reportlab.platypus import PageBreak

from reportlab.lib import colors
from reportlab.lib.units import cm


from django.utils.translation import gettext_lazy as _

from ..util import get_substance_label
from ..util import p_c
from ..util import p_l
from ..util import page_title
from ..util import STYLES
from ..util import TABLE_STYLES


TABLE_IMPORTS_HEADER = (
    (
        p_c(_('Group')),
        p_c(_('Substance')),
        p_c(_('Country of destination of exports')),
        p_c(_('Total Quantity Exported for All Uses')),
        '',
        p_c(_('Quantity of new substances exported as feedstock')),
        p_c(_('Quantity of new substance exported for exempted essential,'
              'critical, high-ambient-temperature or other uses')),
        '',
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
)


TABLE_ROW_EMPTY = (
    (
        _('No data.'),
        '',
        '',
        '',
        '',
        '',
        '',
        '',
    ),
)


TABLE_ROW_EMPTY_STYLE = (
    ('SPAN', (0, 2), (-1, 2)),
    ('VALIGN', (0, 2), (-1, 2), 'MIDDLE'),
    ('ALIGN', (0, 2), (-1, 2), 'CENTER'),
)


TABLE_IMPORTS_HEADER_STYLE = (
    ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
    ('TOPPADDING', (6,2), (7, -1), 10),
    ('VALIGN', (0, 0), (-1, 1), 'MIDDLE'),
    ('VALIGN', (0, 2), (5, -1), 'MIDDLE'),
    ('VALIGN', (6, 2), (7, -1), 'TOP'),
    ('ALIGN', (0, 2), (5, -1), 'CENTER'),
    ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
    ('SPAN', (0, 0), (0, 1)),
    ('SPAN', (1, 0), (1, 1)),
    ('SPAN', (2, 0), (2, 1)),
    ('SPAN', (3, 0), (4, 0)),
    ('SPAN', (5, 0), (5, 1)),
    ('SPAN', (6, 0), (7, 0)),
)


def to_row_substance(obj):
    substance = obj.substance

    quantities = (
        obj.quantity_essential_uses or 0,
        obj.quantity_critical_uses or 0,
        obj.quantity_high_ambient_temperature or 0,
        obj.quantity_laboratory_analytical_uses or 0,
        obj.quantity_process_agent_uses or 0,
        obj.quantity_other_uses or 0,
    )
    q_label = get_substance_label(quantities, type='quantity')
    sum_quantities = sum(quantities)

    decisions = (
        obj.decision_essential_uses,
        obj.decision_critical_uses,
        obj.decision_high_ambient_temperature,
        obj.decision_laboratory_analytical_uses,
        obj.decision_process_agent_uses,
        obj.decision_other_uses,
    )
    d_label = get_substance_label(decisions, type='decision', list_font_size=9)

    q_polyols = (
        p_l('Polyols quantity'),
        p_l(str(obj.quantity_polyols))
    ) if obj.quantity_polyols else ()

    dest_party = obj.destination_party.name if obj.destination_party else ""

    return (
        substance.group.group_id,
        p_l(substance.name),
        p_l(dest_party),
        str(obj.quantity_total_new or ''),
        str(obj.quantity_total_recovered or ''),
        str(obj.quantity_feedstock or ''),
        (p_l(str(sum_quantities or ''), fontName='Helvetica-Bold'),) +
        (q_label,) + q_polyols,
        (d_label,)
    )


def mk_table_substances(submission):
    # TODO: differentiate between blends and substances
    exports = submission.article7exports.filter(blend_item__isnull=True)
    return map(to_row_substance, exports)


def mk_table_blends(submission):
    exports = submission.article7exports.filter(blend_item__isnull=False)
    return map(to_row_substance, exports)


def table_from_data(data):
    return Table(
        TABLE_IMPORTS_HEADER + (data or TABLE_ROW_EMPTY),
        style=(
            TABLE_IMPORTS_HEADER_STYLE + TABLE_STYLES + (
                () if data else TABLE_ROW_EMPTY_STYLE
            )
        ),
        repeatRows=2  # repeat header on page break
    )


def export_exports(submission):
    table_substances = tuple(mk_table_substances(submission))
    table_blends = tuple(mk_table_blends(submission))

    return (
        PageBreak(),
        page_title(_('EXPORTS')),
        p_c(_(
            'Annexes A, B, C and E substances in metric tonnes (not ODP tonnes)'
        ), fontSize=10),
        Spacer(1, cm),
        Paragraph(_('2.1 Substances'), STYLES['Heading2']),
        table_from_data(table_substances),
        PageBreak(),
        Paragraph(_('2.2 Blends'), STYLES['Heading2']),
        table_from_data(table_blends),
    )
