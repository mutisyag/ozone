from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus import Table
from reportlab.platypus import PageBreak

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch


from django.utils.translation import gettext_lazy as _

from ..util import p_c
from ..util import p_l
from ..util import page_title
from ..util import STYLES
from ..util import TABLE_STYLES


TABLE_IMPORTS_HEADER = (
    (
        p_c(_('Group')),
        p_c(_('Substance')),
        p_c(_('Quantity destroyed')),
        p_c(_('Remarks (party)')),
        p_c(_('Remarks (secretariat)')),
    ),
)


TABLE_ROW_EMPTY = (
    (
        _('No data.'),
        '',
        '',
        '',
        '',
    ),
)


TABLE_ROW_EMPTY_STYLE = (
    ('SPAN', (0, 1), (-1, 1)),
    ('VALIGN', (0, 1), (-1, 1), 'MIDDLE'),
    ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
)


TABLE_IMPORTS_HEADER_STYLE = (
    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
    ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
)


def to_row_substance(obj):
    substance = obj.substance

    return (
        substance.group.group_id,
        p_l(substance.name),
        p_l(str(obj.quantity_destroyed)),
        str(obj.remarks_party or ''),
        str(obj.remarks_os or ''),
    )


def mk_table_substances(submission):
    # TODO: differentiate between blends and substances
    destruction = submission.article7destructions.filter(blend_item__isnull=True)
    return map(to_row_substance, destruction)


def mk_table_blends(submission):
    destruction = submission.article7destructions.filter(blend_item__isnull=False)
    return map(to_row_substance, destruction)


def table_from_data(data):
    return Table(
        TABLE_IMPORTS_HEADER + (data or TABLE_ROW_EMPTY),
        style=(
            TABLE_IMPORTS_HEADER_STYLE + TABLE_STYLES + (
                () if data else TABLE_ROW_EMPTY_STYLE
            )
        ),
        repeatRows=2  # repeat header on page break
    )


def export_destruction(submission):
    table_substances = tuple(mk_table_substances(submission))
    table_blends = tuple(mk_table_blends(submission))

    return (
        # TODO: Add explanatory texts.
        PageBreak(),
        page_title(_('QUANTITY OF SUBSTANCES DESTROYED ')),
        Paragraph(_('4.1 Substances'), STYLES['Heading2']),
        table_from_data(table_substances),
        PageBreak(),
        Paragraph(_('4.2 Blends'), STYLES['Heading2']),
        table_from_data(table_blends),
    )
