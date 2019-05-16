from django.utils.translation import gettext_lazy as _

from .imp_exp_helper import big_table_row
from .imp_exp_helper import component_row

from ..util import get_comments_section
from ..util import mk_table_blends
from ..util import mk_table_substances
from ..util import page_title_section
from ..util import table_from_data
from ..util import TABLE_STYLES

from .constants import TABLE_BLENDS_COMP_HEADER
from .constants import TABLE_BLENDS_COMP_STYLE
from .constants import TABLE_BLENDS_COMP_WIDTHS
from .constants import TABLE_IMPORTS_EXPORTS_HEADER
from .constants import TABLE_IMPORTS_EXPORTS_HEADER_STYLE
from .constants import TABLE_IMPORTS_EXPORTS_BL_WIDTHS
from .constants import TABLE_IMPORTS_EXPORTS_SUBS_WIDTHS


def export_exports(submission):
    grouping = submission.article7exports

    table_substances = tuple(mk_table_substances(grouping, big_table_row))
    table_blends = tuple(mk_table_blends(
        grouping, big_table_row, component_row, TABLE_BLENDS_COMP_HEADER('export'),
        TABLE_BLENDS_COMP_STYLE, TABLE_BLENDS_COMP_WIDTHS))

    subst_table = table_from_data(
        data=table_substances, isBlend=False,
        header=TABLE_IMPORTS_EXPORTS_HEADER(False, 'export'),
        colWidths=TABLE_IMPORTS_EXPORTS_SUBS_WIDTHS,
        style=(TABLE_IMPORTS_EXPORTS_HEADER_STYLE + TABLE_STYLES),
        repeatRows=2, emptyData=_('No exported substances.')
    )

    blends_table = table_from_data(
        data=table_blends, isBlend=True,
        header=TABLE_IMPORTS_EXPORTS_HEADER(True, 'export'),
        colWidths=TABLE_IMPORTS_EXPORTS_BL_WIDTHS,
        style=(TABLE_IMPORTS_EXPORTS_HEADER_STYLE + TABLE_STYLES),
        repeatRows=2, emptyData=_('No exported blends.')
    )

    return (
        page_title_section(
            title="%s (%s)" % (_('Exports'), _('metric tonnes')),
        ) + (subst_table, blends_table) +
        get_comments_section(submission, 'exports')
    )
