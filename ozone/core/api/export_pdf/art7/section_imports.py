from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus import Table
from reportlab.lib.units import mm

from django.utils.translation import gettext_lazy as _
from functools import partial

from .. import util as u
from .. import constants as c


def get_imports_header(isBlend):
    first_col = 'Type' if isBlend else 'Group'
    second_col = 'Blend' if isBlend else 'Substance'

    return (
        (
            u.p_c(_(first_col)),
            u.p_c(_(second_col)),
            u.p_c(_('Exporting party for quantities reported as imports')),
            u.p_c(_('Total Quantity Imported for All Uses')),
            '',
            u.p_c(_('Quantity of new substances imported as feedstock')),
            u.p_c(_('Quantity of new substance imported for exempted essential,'
                  'critical, high-ambient-temperature or other uses')),
            ''
        ),
        (
            '',
            '',
            '',
            u.p_c(_('New')),
            u.p_c(_('Recovered and reclaimed')),
            '',
            u.p_c(_('Quantity')),
            u.p_c(_('Decision / type of use or remark')),
        ),
    )


def big_table_row(obj, isBlend):
    col_1 = obj.blend.type if isBlend else obj.substance.group.group_id
    col_2 = obj.blend.blend_id if isBlend else obj.substance.name

    quantities = u.get_quantities(obj)
    extra_q = u.get_preship_or_polyols_q(obj) if not isBlend else None
    q_cell = u.get_quantity_cell(quantities, extra_q)

    decisions = u.get_decisions(obj)
    d_label = u.get_substance_label(decisions, type='decision',
                                    list_font_size=9)

    return (
        col_1,
        col_2,
        obj.source_party.name,
        obj.quantity_total_new,
        obj.quantity_total_recovered,
        obj.quantity_feedstock,
        q_cell,
        (d_label,)
    )

def component_row(component, blend):

    ptg = component.percentage
    q_sum = sum(u.get_quantities(blend))*ptg

    return (
        component.component_name,
        u.p_c('<b>{}%</b>'.format(round(ptg*100,1))),
        str(round(blend.quantity_total_new * ptg)),
        format(blend.quantity_total_recovered * ptg, '.2f'),
        format(blend.quantity_feedstock * ptg, '.3g'),
        str(q_sum) if q_sum != 0.0 else ''
    )


def mk_table_substances(submission):
    # Excluding items with no substance,
    # then getting the ones that are not a blend_item
    imports = submission.article7imports.exclude(substance=None)
    row = partial(big_table_row, isBlend=False)
    return map(row, imports.filter(blend_item=None))


def mk_table_blends(submission):
    imports = submission.article7imports.filter(substance=None)
    row = partial(big_table_row, isBlend=True)
    blends = []

    for blend_row in map(row, imports):

        # Getting the blend object based on the id
        blend = imports.filter(blend__blend_id=blend_row[1]).first()
        row_comp = partial(component_row, blend=blend)
        data = tuple(map(row_comp, blend.blend.components.all()))

        blends.append(blend_row)
        blends.append(
            (
                (Spacer(7, mm),
                 Table(
                    c.TABLE_BLENDS_COMP_HEADER + data,
                    style=c.TABLE_BLENDS_COMP_STYLE,
                    colWidths=c.TABLE_BLENDS_COMP_WIDTHS,
                 ),
                 Spacer(7, mm))
            ,)
        )

    return blends


def table_from_data(data, isBlend):
    header = get_imports_header(isBlend)
    col_widths = c.TABLE_IMPORTS_EXPORTS_BL_WIDTHS if isBlend \
        else c.TABLE_IMPORTS_EXPORTS_SUBS_WIDTHS
    style = (
        c.TABLE_IMPORTS_EXPORTS_HEADER_STYLE + c.TABLE_STYLES + (
            () if data else c.TABLE_ROW_EMPTY_STYLE_IMP_EXP
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
        header + (data or c.TABLE_ROW_EMPTY_IMP_EXP),
        colWidths=col_widths,
        style=style,
        repeatRows=2  # repeat header on page break
    )


def export_imports(submission):
    table_substances = tuple(mk_table_substances(submission))
    table_blends = tuple(mk_table_blends(submission))

    imports_page = (
        Paragraph(_('1.1 Substances'), u.STYLES['Heading2']),
        table_from_data(table_substances, isBlend=False),
        PageBreak(),
        Paragraph(_('1.2 Blends'), u.STYLES['Heading2']),
        table_from_data(table_blends, isBlend=True),
        PageBreak(),
    )

    return u.page_title_section(
        title=_('IMPORTS'),
        explanatory= _(
            'Annexes A, B, C and E substances in metric tonnes (not ODP tonnes)'
        )
    ) + imports_page
