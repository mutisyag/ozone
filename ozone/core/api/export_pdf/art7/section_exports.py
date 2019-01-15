from reportlab.platypus import Paragraph
from reportlab.platypus import Table
from reportlab.platypus import PageBreak

from django.utils.translation import gettext_lazy as _

from ..util import get_preship_or_polyols_q
from ..util import get_decisions
from ..util import get_quantities
from ..util import get_quantity_cell
from ..util import get_substance_label
from ..util import p_c
from ..util import p_l
from ..util import page_title_section
from ..util import STYLES
from ..util import TABLE_IMPORTS_EXPORTS_COL_WIDTHS as COL_WIDTHS
from ..util import TABLE_IMPORTS_EXPORTS_HEADER_STYLE
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


def to_row_substance(obj):
    substance = obj.substance

    quantities = get_quantities(obj)
    extra_q = get_preship_or_polyols_q(obj)
    q_cell = get_quantity_cell(quantities, extra_q)

    decisions = get_decisions(obj)
    d_label = get_substance_label(decisions, type='decision', list_font_size=9)

    dest_party = obj.destination_party.name if obj.destination_party else ""

    return (
        substance.group.group_id,
        p_l(substance.name),
        p_l(dest_party),
        str(obj.quantity_total_new or ''),
        str(obj.quantity_total_recovered or ''),
        str(obj.quantity_feedstock or ''),
        q_cell,
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
        colWidths=COL_WIDTHS,
        style=(
            TABLE_IMPORTS_EXPORTS_HEADER_STYLE + TABLE_STYLES + (
                () if data else TABLE_ROW_EMPTY_STYLE
            )
        ),
        repeatRows=2,  # repeat header on page break
    )


def export_exports(submission):
    table_substances = tuple(mk_table_substances(submission))
    table_blends = tuple(mk_table_blends(submission))

    exports_page = (
        Paragraph(_('2.1 Substances'), STYLES['Heading2']),
        table_from_data(table_substances),
        PageBreak(),
        Paragraph(_('2.2 Blends'), STYLES['Heading2']),
        table_from_data(table_blends),
        PageBreak(),
    )

    return page_title_section(
        title=_('EXPORTS'),
        explanatory=_(
            'Annexes A, B, C and E substances in metric tonnes (not ODP tonnes)'
        )
    ) + exports_page
