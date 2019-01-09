from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus import Table

from reportlab.lib import colors
from reportlab.lib.units import inch


from django.utils.translation import gettext_lazy as _

from ..util import p_c
from ..util import p_l
from ..util import STYLES
from ..util import TABLE_STYLES


TABLE_IMPORTS_HEADER = (
    (
        p_c(_('Group')),
        p_c(_('Substance')),
        p_c(_('Exporting party for quantities reported as imports')),
        p_c(_('Total Quantity Imported for All Uses')),
        '',
        p_c(_('Quantity of new substances imported as feedstock')),
        p_c(_('Quantity of new substance imported for exempted essential,'
              'critical, high-ambient-temperature or other uses')),
        ''
    ),
    (
        '',
        '',
        '',
        p_c(_('New')),
        p_c(_('Recovered and reclaimed')),
        '',
        p_c(_('Quantity')),
        p_c(_('Decision / type of use or remark')),
    ),
)


TABLE_IMPORTS_HEADER_STYLE = (
    ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
    ('VALIGN', (0, 0), (-1, 1), 'MIDDLE'),
    ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
    ('SPAN', (0, 0), (0, 1)),
    ('SPAN', (1, 0), (1, 1)),
    ('SPAN', (2, 0), (2, 1)),
    ('SPAN', (3, 0), (4, 0)),
    ('SPAN', (5, 0), (5, 1)),
    ('SPAN', (6, 0), (7, 0)),
)


def to_row_substance(obj):
    substance = obj.substance

    _q_pre_ship = obj.quantity_quarantine_pre_shipment
    q_pre_ship = (
        p_l(f'Quantity of new {substance.name} '
            'imported to be used for QPS applications'),
        p_l(str(_q_pre_ship))
    ) if _q_pre_ship else ()

    return (
        substance.group.group_id,
        p_l(substance.name),
        p_l(obj.source_party.name),
        str(obj.quantity_total_new or ''),
        str(obj.quantity_total_recovered or ''),
        str(obj.quantity_feedstock or ''),
        (p_l(str(obj.quantity_essential_uses or '')), ) + q_pre_ship,
        str(obj.decision_essential_uses or '')
    )


def mk_table_substances(submission):
    # TODO: differentiate between blends and substances
    imports = submission.article7imports.all()
    return map(to_row_substance, imports)


def export_imports(submission):
    table_substances = tuple(mk_table_substances(submission))
    return (
        # TODO: Add page headings, explanatory texts.
        Paragraph(_('1.1 Substances'), STYLES['Heading2']),
        Table(
            TABLE_IMPORTS_HEADER + table_substances,
            style=TABLE_IMPORTS_HEADER_STYLE + TABLE_STYLES,
            repeatRows=2
        ),
        Spacer(1, inch),
        Paragraph(_('1.2 Blends'), STYLES['Heading2']),
        Table(
            TABLE_IMPORTS_HEADER,  # TODO: export blends
            style=TABLE_IMPORTS_HEADER_STYLE + TABLE_STYLES,
            repeatRows=2
        ),
    )
