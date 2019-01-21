from django.utils.translation import gettext_lazy as _
from reportlab.platypus import Paragraph
from reportlab.platypus import PageBreak

from ..util import get_comments_section
from ..util import get_decisions
from ..util import get_preship_or_polyols_q
from ..util import get_quantity_cell
from ..util import get_quantities
from ..util import get_substance_label
from ..util import p_l
from ..util import page_title_section
from ..util import STYLES
from ..util import TABLE_STYLES
from ..util import table_from_data


from .constants import TABLE_ROW_EMPTY_PROD
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
    d_label = get_substance_label(decisions, type='decision', list_font_size=9)

    return (
        substance.group.group_id,
        p_l(substance.name),
        str(obj.quantity_total_produced or ''),
        str(obj.quantity_feedstock or ''),
        q_cell,
        (d_label,),
        str(obj.quantity_article_5 or '')
    )

def mk_table_substances(submission):
    production = submission.article7productions.all()
    return map(to_row_substance, production)

def mk_table_substances_fii(submission):
    # TODO: Differentiation between FII and non-FII does
    # not appear to be implemented yet.
    return []


def export_production(submission):
    table_substances = tuple(mk_table_substances(submission))
    table_substances_fii = tuple(mk_table_substances_fii(submission))

    comments_section = get_comments_section(submission, 'production')

    style = lambda data: (
        TABLE_STYLES + (
        () if data else (
            ('SPAN', (0, 2), (-1, 2)), (('ALIGN', (0, 2), (-1, 2), 'CENTER'))
        )
    )
    )

    subst_table = table_from_data(
        data=table_substances, isBlend=False,
        header=TABLE_PROD_HEADER,
        colWidths=TABLE_PROD_WIDTH,
        style=style(table_substances)+TABLE_PROD_HEADER_STYLE,
        repeatRows=2, emptyData=TABLE_ROW_EMPTY_PROD
    )

    fii_table = table_from_data(
        data=table_substances_fii, isBlend=False,
        header=TABLE_PROD_HEADER_FII,
        colWidths=TABLE_PROD_WIDTH,
        style=style(table_substances_fii)+TABLE_PROD_HEADER_STYLE_FII,
        repeatRows=2, emptyData=TABLE_ROW_EMPTY_PROD
    )

    prod_page = (
        Paragraph(_('3.1 Substances'), STYLES['Heading2']),
        subst_table,
        PageBreak(),
        Paragraph(_('3.1.1 Substances - group FII'), STYLES['Heading2']),
        fii_table,
        PageBreak(),
        Paragraph(_('3.3 Comments'), STYLES['Heading2'])
    )

    return page_title_section(
        title=_('PRODUCTION'),
        explanatory=_(
            'in tonnes (not ODP or GWP tonnes) Annex A, B, C, E and F '
            'substances'
        )
    ) + prod_page + comments_section
