from django.utils.translation import gettext_lazy as _
from reportlab.platypus import Paragraph

from ..util import get_big_float
from ..util import get_comments_section
from ..util import get_decisions
from ..util import get_preship_or_polyols_q
from ..util import get_quantity_cell
from ..util import get_quantities
from ..util import get_substance_label
from ..util import p_c
from ..util import TABLE_STYLES
from ..util import table_from_data
from ..util import h2_style

from .constants import TABLE_PROD_HEADER
from .constants import TABLE_PROD_HEADER_FII
from .constants import TABLE_PROD_HEADER_STYLE
from .constants import TABLE_PROD_HEADER_STYLE_FII
from .constants import TABLE_PROD_WIDTH


def to_row_substance(obj):
    substance = obj.substance

    quantities = get_quantities(obj)
    extra_q = get_preship_or_polyols_q(obj)
    q_cell = get_quantity_cell(quantities, extra_q)

    decisions = get_decisions(obj)
    d_label = get_substance_label(decisions, type='decision')

    return (
        substance.group.group_id,
        p_c(_(substance.name)),
        p_c(get_big_float(obj.quantity_total_produced or '')),
        p_c(get_big_float(obj.quantity_feedstock or '')),
        q_cell,
        (d_label,),
        p_c(get_big_float(obj.quantity_article_5 or ''))
    )


def mk_table_substances(submission):
    # Exclude annex F/II substances, shown separately
    production = submission.article7productions.exclude(
        substance__is_captured=True
    )
    return map(to_row_substance, production)


def mk_table_substances_fii(submission):
    production = submission.article7productions.filter(
        substance__is_captured=True
    )
    return map(to_row_substance, production)


def export_production(submission):
    table_substances = tuple(mk_table_substances(submission))
    table_substances_fii = tuple(mk_table_substances_fii(submission))

    subtitle = Paragraph(
        "%s (%s)" % (_('Production'), _('metric tonnes')),
        h2_style
    )

    subst_table = table_from_data(
        data=table_substances, isBlend=False,
        header=TABLE_PROD_HEADER,
        colWidths=TABLE_PROD_WIDTH,
        style=TABLE_STYLES+TABLE_PROD_HEADER_STYLE,
        repeatRows=2, emptyData=_('No F/I substances produced.')
    )

    fii_table = table_from_data(
        data=table_substances_fii, isBlend=False,
        header=TABLE_PROD_HEADER_FII,
        colWidths=TABLE_PROD_WIDTH,
        style=TABLE_STYLES+TABLE_PROD_HEADER_STYLE_FII,
        repeatRows=2, emptyData=_('No F/II substances produced.')
    )

    return (subtitle, subst_table, fii_table)
    + get_comments_section(submission, 'production')
