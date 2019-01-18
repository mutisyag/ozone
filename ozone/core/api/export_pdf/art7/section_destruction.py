from django.utils.translation import gettext_lazy as _
from functools import partial

from reportlab.platypus import Paragraph
from reportlab.platypus import PageBreak

from ..constants import TABLE_DEST_HEADER
from ..constants import TABLE_DEST_HEADER_STYLE
from ..constants import TABLE_DEST_COMP_HEADER
from ..constants import TABLE_DEST_COMP_WIDTH
from ..constants import TABLE_DEST_WIDTH
from ..constants import TABLE_ROW_EMPTY_DEST
from ..constants import TABLE_ROW_EMPTY_STYLE_DEST
from ..constants import TABLE_BLENDS_COMP_STYLE
from ..util import p_c
from ..util import p_l
from ..util import page_title_section
from ..util import table_from_data
from ..util import table_with_blends
from ..util import STYLES
from ..util import TABLE_STYLES


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

    blends = map(row, destructions)

    return table_with_blends(
        blends=blends,
        grouping=destructions,
        make_component=component_row,
        header=TABLE_DEST_COMP_HEADER,
        style=TABLE_BLENDS_COMP_STYLE,
        widths=TABLE_DEST_COMP_WIDTH
    )

def export_destruction(submission):
    table_substances = tuple(mk_table_substances(submission))
    table_blends = tuple(mk_table_blends(submission))

    style = lambda data: (
        TABLE_DEST_HEADER_STYLE + TABLE_STYLES + (
            () if data else TABLE_ROW_EMPTY_STYLE_DEST
        )
    )

    subst_table = table_from_data(
        data=table_substances, isBlend=False,
        header=TABLE_DEST_HEADER(False),
        colWidths=TABLE_DEST_WIDTH,
        style=style(table_substances),
        repeatRows=1, emptyData=TABLE_ROW_EMPTY_DEST
    )

    blends_table = table_from_data(
        data=table_blends, isBlend=True,
        header=TABLE_DEST_HEADER(True),
        colWidths=TABLE_DEST_WIDTH,
        style=style(table_blends),
        repeatRows=1, emptyData=TABLE_ROW_EMPTY_DEST
    )

    destr_page = (
        Paragraph(_('4.1 Substances'), STYLES['Heading2']),
        subst_table,
        PageBreak(),
        Paragraph(_('4.2 Blends'), STYLES['Heading2']),
        blends_table,
        PageBreak(),
    )

    return page_title_section(
        title=_('QUANTITY OF SUBSTANCES DESTROYED '),
        explanatory=_(
            'in tonnes (not ODP or GWP tonnes) Annex A, B, C, E and F substances'
        )
    ) + destr_page
