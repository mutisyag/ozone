from reportlab.platypus import Paragraph
from reportlab.platypus import Table
from reportlab.platypus import PageBreak
from reportlab.lib import colors
from reportlab.lib.units import cm

from django.utils.translation import gettext_lazy as _

from ..util import get_decisions
from ..util import get_preship_or_polyols_q
from ..util import get_quantity_cell
from ..util import get_quantities
from ..util import get_substance_label
from ..util import p_c
from ..util import p_l
from ..util import page_title_section
from ..util import STYLES
from ..util import TABLE_STYLES

from ..constants import TABLE_ROW_EMPTY_STYLE_IMP_EXP


TABLE_PROD_HEADER = (
    (
        p_c(_('Group')),
        p_c(_('Substance')),
        p_c(_('Total production for all uses')),
        p_c(_('Production for feedstock uses within your country')),
        p_c(_('Production for exempted essential, '
              'critical or other uses within your country')),
        '',
        p_c(_('Production for supply to Article 5 countries in '
              'accordance with Articles 2A 2H and 5')),
    ),
    (
        '',
        '',
        '',
        '',
        p_c(_('Quantity')),
        p_c(_('Decision / type of use')),
        '',
    ),
)

TABLE_ROW_EMPTY = (
    (
        _('No data.'),
        '',
        '',
        '',
        '',
        '',
        '',
    ),
)


TABLE_PRODUCTION_HEADER_STYLE = (
    ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
    ('VALIGN', (0, 0), (-1, 1), 'MIDDLE'),
    ('VALIGN', (0, 2), (3, -1), 'MIDDLE'),
    ('VALIGN', (5, 2), (6, -1), 'MIDDLE'),
    ('ALIGN', (0, 2), (3, -1), 'CENTER'),
    ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
    ('ALIGN', (6, 2), (6, -1), 'CENTER'),
    ('SPAN', (0, 0), (0, 1)),
    ('SPAN', (1, 0), (1, 1)),
    ('SPAN', (2, 0), (2, 1)),
    ('SPAN', (3, 0), (3, 1)),
    ('SPAN', (4, 0), (5, 0)),
    ('SPAN', (6, 0), (6, 1)),
)

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
    imports = submission.article7productions.all()
    return map(to_row_substance, imports)

def mk_table_substances_fii(submission):
    # TODO: Differentiation between FII and non-FII does
    # not appear to be implemented yet.
    return []

def table_from_data(data):
    col_widths =  list(map(lambda x: x * cm, [1.3, 4, 2, 2, 7, 7, 4]))
    return Table(
        TABLE_PROD_HEADER + (data or TABLE_ROW_EMPTY),
        colWidths=col_widths,
        style=(
            TABLE_PRODUCTION_HEADER_STYLE + TABLE_STYLES + (
                () if data else TABLE_ROW_EMPTY_STYLE_IMP_EXP
            )
        ),
        repeatRows=2  # repeat header on page break
    )

def export_production(submission):
    table_substances = tuple(mk_table_substances(submission))
    table_substances_fii = tuple(mk_table_substances_fii(submission))

    prod_page = (
        Paragraph(_('3.1 Substances'), STYLES['Heading2']),
        table_from_data(table_substances),
        PageBreak(),
        Paragraph(_('3.1.1 Substances - group FII'), STYLES['Heading2']),
        table_from_data(table_substances_fii),
        PageBreak()
    )

    return page_title_section(
        title=_('PRODUCTION'),
        explanatory=_(
            'in tonnes (not ODP or GWP tonnes) Annex A, B, C, E and F '
            'substances'
        )
    ) + prod_page
