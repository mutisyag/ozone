from django.utils.translation import gettext_lazy as _
from reportlab.platypus import Paragraph

from .constants import TABLE_EMISSIONS_HEADER
from .constants import TABLE_EMISSIONS_HEADER_STYLE

from ..util import get_big_float
from ..util import get_comments_section
from ..util import p_c
from ..util import h2_style
from ..util import table_from_data
from ..util import TABLE_STYLES


def to_row_facility(obj):
    fields = (
        obj.quantity_generated,
        obj.quantity_captured_all_uses,
        obj.quantity_captured_feedstock,
        obj.quantity_captured_for_destruction,
        obj.quantity_feedstock,
        obj.quantity_destroyed,
        obj.quantity_emitted,
    )
    return (
        p_c(obj.facility_name),
    ) + tuple(
        p_c(get_big_float(field))
        for field in fields
    )


def export_emission(submission):
    data = submission.article7emissions.all()
    if len(data) == 0:
        return tuple()

    subtitle = Paragraph(
        "%s (%s)" % (_("Emissions of HFC-23"), _("metric tonnes")),
        h2_style
    )

    table_facilities = tuple(map(to_row_facility, data))

    facilities_table = table_from_data(
        data=table_facilities, isBlend=False,
        header=TABLE_EMISSIONS_HEADER,
        colWidths=None, style=TABLE_EMISSIONS_HEADER_STYLE + TABLE_STYLES,
        repeatRows=2, emptyData=_('No emissions.')
    )

    return (subtitle, facilities_table,)
    + get_comments_section(submission, 'emissions')
