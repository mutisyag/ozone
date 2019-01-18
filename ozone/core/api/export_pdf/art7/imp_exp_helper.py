from ..util import get_decisions
from ..util import get_preship_or_polyols_q
from ..util import get_quantities
from ..util import get_quantity_cell
from ..util import get_substance_label
from ..util import p_c

from django.utils.translation import gettext_lazy as _


def big_table_row(obj, isBlend):
    col_1 = obj.blend.type if isBlend else obj.substance.group.group_id
    col_2 = obj.blend.blend_id if isBlend else obj.substance.name

    quantities = get_quantities(obj)
    extra_q = get_preship_or_polyols_q(obj) if not isBlend else None
    q_cell = get_quantity_cell(quantities, extra_q)

    decisions = get_decisions(obj)
    d_label = get_substance_label(decisions, type='decision',
                                    list_font_size=9)

    party = obj.source_party if hasattr(obj, 'source_party') else \
        obj.destination_party if obj.destination_party else ""

    return (
        p_c(_(col_1)),
        p_c(_(col_2)),
        p_c(_(party.name if hasattr(party, 'name') else '')),
        p_c(str(obj.quantity_total_new or '')),
        p_c(str(obj.quantity_total_recovered or '')),
        obj.quantity_feedstock,
        q_cell,
        (d_label,)
    )

def component_row(component, blend):
    ptg = component.percentage
    q_sum = sum(get_quantities(blend)) * ptg

    return (
        component.component_name,
        p_c('<b>{}%</b>'.format(round(ptg * 100, 1))),
        str(round(blend.quantity_total_new * ptg)),
        format(blend.quantity_total_recovered * ptg, '.2f'),
        format(blend.quantity_feedstock * ptg, '.3g'),
        str(q_sum) if q_sum != 0.0 else ''
    )
