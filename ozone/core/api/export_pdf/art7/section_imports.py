from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus import Table
from reportlab.lib.units import mm

from django.utils.translation import gettext_lazy as _
from functools import partial

from ..util import get_decisions
from ..util import get_preship_or_polyols_q
from ..util import get_quantity_cell
from ..util import get_quantities
from ..util import get_substance_label
from ..util import p_c
from ..util import p_l
from ..util import page_title_section

from ..util import STYLES
from ..constants import TABLE_IMPORTS_EXPORTS_SUBS_WIDTHS as SUBS_WIDTHS
from ..constants import TABLE_IMPORTS_EXPORTS_BL_WIDTHS as BLEND_WIDTHS
from ..constants import TABLE_IMPORTS_EXPORTS_HEADER_STYLE
from ..constants import TABLE_STYLES
from ..constants import TABLE_BLENDS_COMP_HEADER
from ..constants import TABLE_BLENDS_COMP_STYLE
from ..constants import TABLE_BLENDS_COMP_WIDTHS
from ..constants import TABLE_ROW_EMPTY_IMP_EXP
from ..constants import TABLE_ROW_EMPTY_STYLE_IMP_EXP


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
    # TODO: merge with to_row_substance
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

def to_row_component(component, blend):

    ptg = component.percentage
    q_sum = sum(get_quantities(blend))*ptg

    return (
        component.component_name,
        p_c('<b>{}%</b>'.format(round(ptg*100,1))),
        str(round(blend.quantity_total_new * ptg)),
        format(blend.quantity_total_recovered * ptg, '.2f'),
        format(blend.quantity_feedstock * ptg, '.3g'),
        str(q_sum) if q_sum != 0.0 else ''
    )


def mk_table_substances(submission):
    # Excluding items with no substance,
    # then getting the ones that are not a blend_item
    imports = submission.article7imports.exclude(substance=None)
    return map(to_row_substance, imports.filter(blend_item=None))


def mk_table_blends(submission):
    imports = submission.article7imports.filter(substance=None)
    blends = []
    for blend_row in map(to_row_blend, imports):

        # Getting the blend object based on the id
        blend = imports.filter(blend__blend_id=blend_row[1]).first()
        row_comp = partial(to_row_component, blend=blend)
        data = tuple(map(row_comp, blend.blend.components.all()))

        blends.append(blend_row)
        blends.append(
            (
                (Spacer(7, mm),
                 Table(
                    TABLE_BLENDS_COMP_HEADER + data,
                    style=TABLE_BLENDS_COMP_STYLE,
                    colWidths=TABLE_BLENDS_COMP_WIDTHS,
                 ),
                 Spacer(7, mm))
            ,)
        )

    return blends


def table_from_data(data, isBlend):
    header = get_imports_header(isBlend)
    col_widths = BLEND_WIDTHS if isBlend else SUBS_WIDTHS
    style = (
        TABLE_IMPORTS_EXPORTS_HEADER_STYLE + TABLE_STYLES + (
            () if data else TABLE_ROW_EMPTY_STYLE_IMP_EXP
        )
    )

    # Spanning all columns for the blend components rows
    if isBlend:
        rows = len(data)+2
        for row_idx in range(3, rows, 2):
            style += (
                ('SPAN', (0, row_idx), (-1, row_idx)),
            )

    return Table(
        header + (data or TABLE_ROW_EMPTY_IMP_EXP),
        colWidths=col_widths,
        style=style,
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

