from django.utils.translation import gettext_lazy as _
from functools import partial

from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus import Table
from reportlab.platypus import PageBreak
from reportlab.lib.units import cm
from reportlab.lib.units import mm


from ..constants import TABLE_DEST_HEADER_STYLE
from ..constants import TABLE_DEST_COMP_HEADER
from ..constants import TABLE_ROW_EMPTY_DEST
from ..constants import TABLE_ROW_EMPTY_STYLE_DEST
from ..constants import TABLE_BLENDS_COMP_STYLE
from ..util import p_c
from ..util import p_l
from ..util import page_title_section
from ..util import STYLES
from ..util import TABLE_STYLES


TABLE_DEST_HEADER = (
    (
        p_c(_('Group')),
        p_c(_('Substance')),
        p_c(_('Quantity destroyed')),
        p_c(_('Remarks (party)')),
        p_c(_('Remarks (secretariat)')),
    ),
)


def big_table_row(obj, isBlend):
    col_1 = obj.blend.type if isBlend else obj.substance.group.group_id
    col_2 = obj.blend.blend_id if isBlend else obj.substance.name

    return (
        col_1,
        col_2,
        p_l(str(obj.quantity_destroyed)),
        str(obj.remarks_party or ''),
        str(obj.remarks_os or ''),
    )

def component_row(component, blend):
    ptg = component.percentage

    return (
        component.substance,
        p_c('<b>{}%</b>'.format(round(ptg * 100, 1))),
        str(blend.quantity_destroyed * ptg)
    )


def mk_table_substances(submission):
    # Excluding items with no substance,
    # then getting the ones that are not a blend
    destruction = submission.article7destructions.exclude(substance=None)
    row = partial(big_table_row, isBlend=False)
    return map(row, destruction.filter(blend_item=None))

def mk_table_blends(submission):
    destructions = submission.article7destructions.filter(substance=None)
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
                     colWidths=list(map(lambda x: x * cm, [6, 5, 6]))
                 ),
                 Spacer(7, mm))
                ,)
        )

    return blends

def table_from_data(data, isBlend):
    style = (
        TABLE_DEST_HEADER_STYLE + TABLE_STYLES + (
            () if data else TABLE_ROW_EMPTY_STYLE_DEST
        )
    )

    # Spanning all columns for the blend components rows
    if isBlend:
        rows = len(data) + 1
        for row_idx in range(2, rows, 2):
            style += (
                ('SPAN', (0, row_idx), (-1, row_idx)),
            )

    return Table(
        TABLE_DEST_HEADER + (data or TABLE_ROW_EMPTY_DEST),
        style=style,
        colWidths=list(map(lambda x: x * cm, [4, 3, 4, 6, 6])),
        repeatRows=1  # repeat header on page break
    )


def export_destruction(submission):
    table_substances = tuple(mk_table_substances(submission))
    table_blends = tuple(mk_table_blends(submission))

    destr_page = (
        Paragraph(_('4.1 Substances'), STYLES['Heading2']),
        table_from_data(table_substances, isBlend=False),
        PageBreak(),
        Paragraph(_('4.2 Blends'), STYLES['Heading2']),
        table_from_data(table_blends, isBlend=True),
        PageBreak(),
    )

    return page_title_section(
        title=_('QUANTITY OF SUBSTANCES DESTROYED '),
        explanatory=_(
            'in tonnes (not ODP or GWP tonnes) Annex A, B, C, E and F substances'
        )
    ) + destr_page
