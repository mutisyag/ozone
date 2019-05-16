from django.utils.translation import gettext_lazy as _

from .constants import TABLE_EMISSIONS_HEADER
from .constants import TABLE_EMISSIONS_HEADER_STYLE

from ..util import get_big_float
from ..util import get_comments_section
from ..util import p_c
from ..util import page_title_section
from ..util import table_from_data
from ..util import TABLE_STYLES


def to_row_facility(obj):
    return (
        p_c(_(obj.facility_name)),
        p_c(_(get_big_float(obj.quantity_generated or ''))),
        p_c(_(get_big_float(obj.quantity_captured_all_uses or ''))),
        p_c(_(get_big_float(obj.quantity_captured_feedstock or ''))),
        p_c(_(get_big_float(obj.quantity_captured_for_destruction or ''))),
        p_c(_(get_big_float(obj.quantity_feedstock or ''))),
        p_c(_(get_big_float(obj.quantity_destroyed or ''))),
        p_c(_(get_big_float(obj.quantity_emitted or ''))),
    )


def export_emission(submission):
    data = submission.article7emissions.all()

    table_facilities = tuple(map(to_row_facility, data))

    facilities_table = table_from_data(
        data=table_facilities, isBlend=False,
        header=TABLE_EMISSIONS_HEADER,
        colWidths=None, style=TABLE_EMISSIONS_HEADER_STYLE + TABLE_STYLES,
        repeatRows=2, emptyData=_('No emissions.')
    )

    return (
        page_title_section(
            title=_("%s (%s)" % ("Emissions of HFC-23", "metric tonnes")),
        ) + (facilities_table,) +
        get_comments_section(submission, 'emissions')
    )
