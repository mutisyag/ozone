from django.utils.translation import gettext_lazy as _
from functools import partial

from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus import Table
from reportlab.platypus import PageBreak
from reportlab.lib.units import cm
from reportlab.lib.units import mm


from ..constants import TABLE_NONP_HEADER_STYLE
from ..constants import TABLE_ROW_EMPTY_NONP
from ..constants import TABLE_NONP_SUBS_WIDTHS
from ..constants import TABLE_NONP_COMP_WIDTHS
from ..constants import TABLE_DEST_COMP_HEADER
from ..constants import TABLE_ROW_EMPTY_STYLE_DEST
from ..constants import TABLE_BLENDS_COMP_STYLE
from ..util import p_c
from ..util import page_title_section
from ..util import STYLES
from ..util import TABLE_STYLES


def get_header(isBlend):
    col_1 = 'Type' if isBlend else 'Group'
    col_2 = 'Blend' if isBlend else 'Substance'

    return (
        (
            p_c(_(col_1)),
            p_c(_(col_2)),
            p_c(_('Exporting party for quantities reported as imports <b>OR</b> Country of destination of exports')),
            p_c(_('Quantity of imports from non-parties')),
            '',
            p_c(_('Quantity of exports from non-parties')),
            '',
            p_c(_('Remarks (party)')),
            p_c(_('Remarks (secretariat)')),
        ),
        (
            '',
            '',
            '',
            p_c(_('New imports')),
            p_c(_('Recovered and reclaimed imports')),
            p_c(_('New exports')),
            p_c(_('Recovered and reclaimed exports')),
            '',
            '',
        )
    )


def big_table_row(obj, isBlend):
    col_1 = obj.blend.type if isBlend else obj.substance.group.group_id
    col_2 = obj.blend.blend_id if isBlend else obj.substance.name

    return (
        col_1,
        col_2,
        obj.trade_party.name if obj.trade_party else '',
        str(obj.quantity_import_new or ''),
        str(obj.quantity_import_recovered or ''),
        str(obj.quantity_export_new or ''),
        str(obj.quantity_export_recovered or ''),
        str(obj.remarks_party or ''),
        str(obj.remarks_os or ''),
    )

def component_row(component, blend):
    ptg = component.percentage

    return (
        component.substance,
        p_c('<b>{}%</b>'.format(round(ptg * 100, 1))),
        str(blend.quantity_import_new * ptg),
        str(blend.quantity_import_recovered * ptg),
        str(blend.quantity_export_new * ptg),
        str(blend.quantity_export_recovered  * ptg),
    )


def mk_table_substances(submission):
    # Excluding items with no substance,
    # then getting the ones that are not a blend
    destruction = submission.article7nonpartytrades.exclude(substance=None)
    row = partial(big_table_row, isBlend=False)
    return map(row, destruction.filter(blend_item=None))

def mk_table_blends(submission):
    destructions = submission.article7nonpartytrades.filter(substance=None)
    row = partial(big_table_row, isBlend=True)

    blends = []

    for blend_row in map(row, destructions):
        # Getting the blend object based on the id
        blend = destructions.filter(blend__blend_id=blend_row[1]).first()
        row_comp = partial(component_row, blend=blend)
        data = tuple(map(row_comp, blend.blend.components.all()))

        blends.append(blend_row)
        blends.append(
            (
                (Spacer(7, mm),
                 Table(
                     TABLE_DEST_COMP_HEADER + data,
                     style=TABLE_BLENDS_COMP_STYLE,
                     colWidths=TABLE_NONP_COMP_WIDTHS
                 ),
                 Spacer(7, mm))
                ,)
        )

    return blends

def table_from_data(data, isBlend):
    header = get_header(isBlend)

    style = (
        TABLE_NONP_HEADER_STYLE + TABLE_STYLES + (
            () if data else TABLE_ROW_EMPTY_STYLE_DEST
        )
    )

    # Spanning all columns for the blend components rows
    if isBlend:
        rows = len(data) + 2
        for row_idx in range(3, rows, 2):
            style += (
                ('SPAN', (0, row_idx), (-1, row_idx)),
            )

    return Table(
        header + (data or TABLE_ROW_EMPTY_NONP),
        style=style,
        colWidths=TABLE_NONP_SUBS_WIDTHS,
        repeatRows=2  # repeat header on page break
    )


def export_nonparty(submission):
    table_substances = tuple(mk_table_substances(submission))
    table_blends = tuple(mk_table_blends(submission))

    nonp_page = (
        Paragraph(_('5.1 Substances'), STYLES['Heading2']),
        table_from_data(table_substances, isBlend=False),
        PageBreak(),
        Paragraph(_('5.2 Blends'), STYLES['Heading2']),
        table_from_data(table_blends, isBlend=True),
        PageBreak(),
    )

    return page_title_section(
        title=_('IMPORTS FROM AND/OR EXPORTS TO NON PARTIES'),
        explanatory=_(
            'in tonnes (not ODP or GWP tonnes) Annex A, B, C and E substances'
        )
    ) + nonp_page
