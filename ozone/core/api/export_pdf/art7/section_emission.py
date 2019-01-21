from django.utils.translation import gettext_lazy as _

from reportlab.platypus import Paragraph
from reportlab.platypus import PageBreak

from ..constants import TABLE_EMISSIONS_HEADER
from ..constants import TABLE_EMISSIONS_HEADER_STYLE
from ..constants import TABLE_ROW_EMPTY_EMISSIONS
from ..constants import TABLE_ROW_EMPTY_STYLE_IMP_EXP


from ..util import get_comments_section
from ..util import p_c
from ..util import page_title_section
from ..util import table_from_data
from ..util import STYLES
from ..util import TABLE_STYLES


def to_row_facility(obj):
    return (
        p_c(_(obj.facility_name)),
        p_c(_(str(obj.quantity_generated or ''))),
        p_c(_(str(obj.quantity_captured_all_uses or ''))),
        p_c(_(str(obj.quantity_captured_feedstock or ''))),
        p_c(_(str(obj.quantity_captured_for_destruction or ''))),
        p_c(_(str(obj.quantity_feedstock or ''))),
        p_c(_(str(obj.quantity_destroyed or ''))),
        p_c(_(str(obj.quantity_emitted or ''))),
    )

def mk_table_facilities(submission):
    emissions = submission.article7emissions.all()
    return map(to_row_facility, emissions)

def export_emission(submission):
    table_facilities = tuple(mk_table_facilities(submission))

    comments_section = get_comments_section(submission, 'emissions')

    style = (
        TABLE_EMISSIONS_HEADER_STYLE + TABLE_STYLES + (
            () if table_facilities else TABLE_ROW_EMPTY_STYLE_IMP_EXP
        )
    )

    facilities_table = table_from_data(
        data=table_facilities, isBlend=False,
        header=TABLE_EMISSIONS_HEADER,
        colWidths=None,
        style=style,
        repeatRows=2, emptyData=TABLE_ROW_EMPTY_EMISSIONS
    )

    emissions_page = (
        Paragraph(_('6.1 Facilities'), STYLES['Heading2']),
        facilities_table,
        PageBreak(),
        Paragraph(_('6.2 Comments'), STYLES['Heading2'])
    )

    return page_title_section(
        title=_('DATA ON QUANTITY OF EMISSIONS OF HFC 23 FROM FACILITIES '
                'MANUFACTURING ANNEX C GROUP I OR ANNEX F SUBSTANCES'),
        explanatory=_(
            'In metric tons, not ODP or CO2-equivalent tonnes.'
        )
    ) + emissions_page + comments_section
