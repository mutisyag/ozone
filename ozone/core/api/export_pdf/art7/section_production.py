from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus import Table
from reportlab.platypus import PageBreak

from reportlab.lib import colors
from reportlab.lib.units import cm


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
        p_c(_('Total production for all uses')),
        p_c(_('Production for feedstock uses within your country')),
        p_c(_('Production for exempted essential, '
              'critical or other uses within your country')),
        '',
        '',
    ),
    (
        '',
        '',
        '',
        '',
        p_c(_('Quantity')),
        p_c(_('Decision / type of use')),
        p_c(_('Production for supply to Article 5 countries in '
              'accordance with Articles 2A 2H and 5')),
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
        '',
    ),
)


TABLE_ROW_EMPTY_STYLE = (
    ('SPAN', (0, 2), (-1, 2)),
    ('VALIGN', (0, 2), (-1, 2), 'MIDDLE'),
    ('ALIGN', (0, 2), (-1, 2), 'CENTER'),
)


TABLE_IMPORTS_HEADER_STYLE = (
    ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
    ('VALIGN', (0, 0), (-1, 1), 'MIDDLE'),
    ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
    ('SPAN', (0, 0), (0, 1)),
    ('SPAN', (1, 0), (1, 1)),
    ('SPAN', (2, 0), (2, 1)),
    ('SPAN', (3, 0), (3, 1)),
    ('SPAN', (4, 0), (5, 0)),
)


def to_row_substance(obj):
    substance = obj.substance

    _q_pre_ship = obj.quantity_quarantine_pre_shipment
    q_pre_ship = (
        p_l(f'Quantity of new {substance.name} '
            'produced to be used for QPS applications'),
        p_l(str(_q_pre_ship))
    ) if _q_pre_ship else ()

    sum_quantities = sum((
        obj.quantity_essential_uses or 0,
        obj.quantity_critical_uses or 0,
        obj.quantity_high_ambient_temperature or 0,
        obj.quantity_laboratory_analytical_uses or 0,
        obj.quantity_process_agent_uses or 0,
        obj.quantity_other_uses or 0,
    ))

    decisions_quantities = (
        obj.decision_essential_uses,
        obj.decision_critical_uses,
        obj.decision_high_ambient_temperature,
        obj.decision_laboratory_analytical_uses,
        obj.decision_process_agent_uses,
        obj.decision_other_uses,
    )

    join_decisions = ', '.join(filter(bool, decisions_quantities))

    return (
        substance.group.group_id,
        p_l(substance.name),
        str(obj.quantity_total_produced or ''),
        str(obj.quantity_feedstock or ''),
        (p_l(str(sum_quantities or '')), ) + q_pre_ship,
        str(join_decisions or ''),
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
    return Table(
        TABLE_IMPORTS_HEADER + (data or TABLE_ROW_EMPTY),
        style=(
            TABLE_IMPORTS_HEADER_STYLE + TABLE_STYLES + (
                () if data else TABLE_ROW_EMPTY_STYLE
            )
        ),
        repeatRows=2  # repeat header on page break
    )


def export_production(submission):
    table_substances = tuple(mk_table_substances(submission))
    table_substances_fii = tuple(mk_table_substances_fii(submission))
    return (
        PageBreak(),
        page_title(_('PRODUCTION')),
        p_c(_(
            'in tonnes (not ODP or GWP tonnes) Annex A, B, C, E and F substances'
        ), fontSize=10),
        Spacer(1, cm),
        Paragraph(_('3.1 Substances'), STYLES['Heading2']),
        table_from_data(table_substances),
        PageBreak(),
        Paragraph(_('3.1.1 Substances - group FII'), STYLES['Heading2']),
        table_from_data(table_substances_fii),
    )
