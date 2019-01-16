from reportlab.platypus import Paragraph
from reportlab.platypus import Table
from reportlab.platypus import PageBreak

from django.utils.translation import gettext_lazy as _

from ..util import get_decisions
from ..util import get_preship_or_polyols_q
from ..util import get_quantity_cell
from ..util import get_quantities
from ..util import get_substance_label
from ..util import p_c
from ..util import p_l
from ..util import page_title_section
from ..util import STYLES
from ..util import TABLE_IMPORTS_EXPORTS_SUBS_WIDTHS as SUBS_WIDTHS
from ..util import TABLE_IMPORTS_EXPORTS_BL_WIDTHS as BLEND_WIDTHS
from ..util import TABLE_IMPORTS_EXPORTS_HEADER_STYLE
from ..util import TABLE_STYLES


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

def get_imports_header(isBlend):
    first_col = 'Type' if isBlend else 'Group'
    second_col = 'Blend' if isBlend else 'Substance'

    return (
        (
            p_c(_(first_col)),
            p_c(_(second_col)),
            p_c(_('Exporting party for quantities reported as imports')),
            p_c(_('Total Quantity Imported for All Uses')),
            '',
            p_c(_('Quantity of new substances imported as feedstock')),
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
    )


def to_row_substance(obj):
    substance = obj.substance

    quantities = get_quantities(obj)
    extra_q = get_preship_or_polyols_q(obj)
    q_cell = get_quantity_cell(quantities, extra_q)

    decisions = get_decisions(obj)
    d_label = get_substance_label(decisions, type='decision', list_font_size=9)

    return (
        substance.group.group_id,
        p_l(substance.name),
        p_l(obj.source_party.name),
        str(obj.quantity_total_new or ''),
        str(obj.quantity_total_recovered or ''),
        str(obj.quantity_feedstock or ''),
        q_cell,
        (d_label,)
    )

def to_row_blend(obj):
    blend = obj.blend

    quantities = get_quantities(obj)
    q_cell = get_quantity_cell(quantities, None)

    decisions = get_decisions(obj)
    d_label = get_substance_label(decisions, type='decision', list_font_size=9)

    return (
        blend.type,
        blend.blend_id,
        obj.source_party.name,
        obj.quantity_total_new,
        obj.quantity_total_recovered,
        obj.quantity_feedstock,
        q_cell,
        (d_label,)
    )


def mk_table_substances(submission):
    # Excluding items with no substance,
    # then getting the ones that are not a blend_item

    imports = submission.article7imports.exclude(substance=None)
    return map(to_row_substance, imports.filter(blend_item=None))


def mk_table_blends(submission):
    imports = submission.article7imports.filter(substance=None)
    return map(to_row_blend, imports)


def table_from_data(data, isBlend):
    header = get_imports_header(isBlend)
    col_widths = BLEND_WIDTHS if isBlend else SUBS_WIDTHS

    return Table(
        header + (data or TABLE_ROW_EMPTY),
        colWidths=col_widths,
        style=(
            TABLE_IMPORTS_EXPORTS_HEADER_STYLE + TABLE_STYLES + (
                () if data else TABLE_ROW_EMPTY_STYLE
            )
        ),
        repeatRows=2  # repeat header on page break
    )


def export_imports(submission):
    table_substances = tuple(mk_table_substances(submission))
    table_blends = tuple(mk_table_blends(submission))

    imports_page = (
        Paragraph(_('1.1 Substances'), STYLES['Heading2']),
        table_from_data(table_substances, isBlend=False),
        PageBreak(),
        Paragraph(_('1.2 Blends'), STYLES['Heading2']),
        table_from_data(table_blends, isBlend=True),
        PageBreak(),
    )

    return page_title_section(
        title=_('IMPORTS'),
        explanatory= _(
            'Annexes A, B, C and E substances in metric tonnes (not ODP tonnes)'
        )
    ) + imports_page

