from django.utils.translation import gettext_lazy as _

from reportlab.platypus import Paragraph

from .constants import TABLE_BLENDS_COMP_STYLE
from .constants import TABLE_NONP_HEADER
from .constants import TABLE_NONP_HEADER_STYLE
from .constants import TABLE_NONP_SUBS_WIDTHS
from .constants import TABLE_NONP_COMP_WIDTHS
from .constants import TABLE_NONP_COMP_HEADER

from ..util import get_big_float
from ..util import get_comments_section
from ..util import mk_table_blends
from ..util import mk_table_substances
from ..util import p_c, p_r
from ..util import page_title_section
from ..util import table_from_data
from ..util import to_precision
from ..util import STYLES
from ..util import TABLE_STYLES


def big_table_row(obj, isBlend):
    col_1 = obj.blend.type if isBlend else obj.substance.group.group_id
    col_2 = obj.blend.blend_id if isBlend else obj.substance.name

    return (
        p_c(_(col_1)),
        p_c(_(col_2)),
        p_c(_(get_big_float(obj.trade_party.name))) if obj.trade_party else '',
        p_c(_(get_big_float(obj.quantity_import_new or ''))),
        p_c(_(get_big_float(obj.quantity_import_recovered or ''))),
        p_c(_(get_big_float(obj.quantity_export_new or ''))),
        p_c(_(get_big_float(obj.quantity_export_recovered or ''))),
        p_c(_(get_big_float(obj.remarks_party or ''))),
        p_c(_(get_big_float(obj.remarks_os or ''))),
    )


def component_row(component, blend):
    ptg = component.percentage

    return (
        component.substance,
        p_c('<b>{}%</b>'.format(round(ptg * 100, 1))),
        to_precision(blend.quantity_import_new * ptg, 3),
        to_precision(blend.quantity_import_recovered * ptg, 3),
        to_precision(blend.quantity_export_new * ptg, 3),
        to_precision(blend.quantity_export_recovered * ptg, 3),
    )


def export_nonparty(submission):
    data = submission.article7nonpartytrades

    table_substances = tuple(mk_table_substances(data, big_table_row))
    table_blends = tuple(mk_table_blends(
        data, big_table_row, component_row, TABLE_NONP_COMP_HEADER,
        TABLE_BLENDS_COMP_STYLE, TABLE_NONP_COMP_WIDTHS
    ))

    subst_table = table_from_data(
        data=table_substances, isBlend=False,
        header=TABLE_NONP_HEADER(False),
        colWidths=TABLE_NONP_SUBS_WIDTHS,
        style=TABLE_NONP_HEADER_STYLE + TABLE_STYLES,
        repeatRows=2, emptyData=_('No substances.')
    )

    blends_table = table_from_data(
        data=table_blends, isBlend=True,
        header=TABLE_NONP_HEADER(True),
        colWidths=TABLE_NONP_SUBS_WIDTHS,
        style=TABLE_NONP_HEADER_STYLE + TABLE_STYLES,
        repeatRows=2, emptyData=_('No blends.')
    )

    return (
        page_title_section(
            title=_("Imports from and/or exports to non-parties"),
        ) + (subst_table, blends_table) +
        get_comments_section(submission, 'nonparty')
    )
