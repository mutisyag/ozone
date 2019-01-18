from django.utils.translation import gettext_lazy as _
from functools import partial

from reportlab.platypus import Paragraph
from reportlab.platypus import PageBreak

from ..constants import TABLE_NONP_HEADER
from ..constants import TABLE_NONP_HEADER_STYLE
from ..constants import TABLE_ROW_EMPTY_NONP
from ..constants import TABLE_NONP_SUBS_WIDTHS
from ..constants import TABLE_NONP_COMP_WIDTHS
from ..constants import TABLE_NONP_COMP_HEADER
from ..constants import TABLE_ROW_EMPTY_STYLE_DEST
from ..constants import TABLE_BLENDS_COMP_STYLE
from ..util import p_c
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
    non_party = submission.article7nonpartytrades.exclude(substance=None)
    row = partial(big_table_row, isBlend=False)
    return map(row, non_party.filter(blend_item=None))

def mk_table_blends(submission):
    non_party = submission.article7nonpartytrades.filter(substance=None)
    row = partial(big_table_row, isBlend=True)

    blends = map(row, non_party)

    return table_with_blends(
        blends=blends,
        grouping=non_party,
        make_component=component_row,
        header=TABLE_NONP_COMP_HEADER,
        style=TABLE_BLENDS_COMP_STYLE,
        widths=TABLE_NONP_COMP_WIDTHS
    )

def export_nonparty(submission):
    table_substances = tuple(mk_table_substances(submission))
    table_blends = tuple(mk_table_blends(submission))

    style = lambda data: (
        TABLE_NONP_HEADER_STYLE + TABLE_STYLES + (
            () if data else TABLE_ROW_EMPTY_STYLE_DEST
        )
    )

    subst_table = table_from_data(
        data=table_substances, isBlend=False,
        header=TABLE_NONP_HEADER(False),
        colWidths=TABLE_NONP_SUBS_WIDTHS,
        style=style(table_substances),
        repeatRows=2, emptyData=TABLE_ROW_EMPTY_NONP
    )

    blends_table = table_from_data(
        data=table_blends, isBlend=True,
        header=TABLE_NONP_HEADER(True),
        colWidths=TABLE_NONP_SUBS_WIDTHS,
        style=style(table_blends),
        repeatRows=2, emptyData=TABLE_ROW_EMPTY_NONP
    )

    nonp_page = (
        Paragraph(_('5.1 Substances'), STYLES['Heading2']),
        subst_table,
        PageBreak(),
        Paragraph(_('5.2 Blends'), STYLES['Heading2']),
        blends_table,
        PageBreak(),
    )

    return page_title_section(
        title=_('IMPORTS FROM AND/OR EXPORTS TO NON PARTIES'),
        explanatory=_(
            'in tonnes (not ODP or GWP tonnes) Annex A, B, C and E substances'
        )
    ) + nonp_page
