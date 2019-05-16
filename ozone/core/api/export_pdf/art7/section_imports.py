from .constants import TABLE_BLENDS_COMP_HEADER
from .constants import TABLE_BLENDS_COMP_STYLE
from .constants import TABLE_BLENDS_COMP_WIDTHS
from .constants import TABLE_IMPORTS_EXPORTS_HEADER
from .constants import TABLE_IMPORTS_EXPORTS_HEADER_STYLE
from .constants import TABLE_IMPORTS_EXPORTS_BL_WIDTHS
from .constants import TABLE_IMPORTS_EXPORTS_SUBS_WIDTHS

from ..util import get_comments_section
from ..util import mk_table_blends
from ..util import mk_table_substances
from ..util import page_title_section
from ..util import table_from_data
from ..util import TABLE_STYLES

from .imp_exp_helper import big_table_row
from .imp_exp_helper import component_row

from django.utils.translation import gettext_lazy as _


def export_imports(submission):
    data = submission.article7imports

    table_substances = tuple(mk_table_substances(data, big_table_row))
    table_blends = tuple(mk_table_blends(
        data, big_table_row, component_row, TABLE_BLENDS_COMP_HEADER('import'),
        TABLE_BLENDS_COMP_STYLE, TABLE_BLENDS_COMP_WIDTHS
    ))

    subst_table = table_from_data(
        data=table_substances, isBlend=False,
        header=TABLE_IMPORTS_EXPORTS_HEADER(False, 'import'),
        colWidths=TABLE_IMPORTS_EXPORTS_SUBS_WIDTHS,
        style=(TABLE_IMPORTS_EXPORTS_HEADER_STYLE + TABLE_STYLES),
        repeatRows=2, emptyData=_('No imported substances.')
    )

    blends_table = table_from_data(
        data=table_blends, isBlend=True,
        header=TABLE_IMPORTS_EXPORTS_HEADER(True, 'import'),
        colWidths=TABLE_IMPORTS_EXPORTS_BL_WIDTHS,
        style=(TABLE_IMPORTS_EXPORTS_HEADER_STYLE + TABLE_STYLES),
        repeatRows=2, emptyData=_('No imported blends.')
    )

    return (
        page_title_section(
            title="%s (%s)" % (_('Imports'), _('metric tonnes')),
        ) + (subst_table, blends_table) +
        get_comments_section(submission, 'imports')
    )
