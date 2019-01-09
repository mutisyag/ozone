from functools import partial

from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib import pagesizes
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle

from django.utils.translation import gettext_lazy as _


PG_SIZE = pagesizes.landscape(pagesizes.A4)

PAGE_HEIGHT = PG_SIZE[1]
PAGE_WIDTH = PG_SIZE[0]

STYLES = getSampleStyleSheet()


def _p(style_name, align, txt):
    style = STYLES[style_name]
    style.alignment = align
    return Paragraph(txt, style)


p_c = partial(_p, 'BodyText', TA_CENTER)
p_l = partial(_p, 'BodyText', TA_LEFT)


TABLE_SUBSTANCES_HEADER = (
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


TABLE_SUBSTANCES_HEADER_STYLE = (
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


TABLE_STYLE = (
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
)


def to_row_art7import(obj):
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
        None  # TODO: decision/type of use or remark
    )


def mk_table_art7import_substances(submission):
    imports = submission.article7imports.all()
    return map(to_row_art7import, imports)


def export_submission(submission):
    buff = BytesIO()

    doc = SimpleDocTemplate(buff, pagesize=PG_SIZE)

    story = []

    table_art7import_substances = tuple(mk_table_art7import_substances(submission))

    story.append(Paragraph(_('1.1 Substances'), STYLES['Heading2']))
    table = Table(
        TABLE_SUBSTANCES_HEADER + table_art7import_substances,
        style=TABLE_SUBSTANCES_HEADER_STYLE + TABLE_STYLE,
        repeatRows=2
    )

    story.append(table)

    doc.build(story)

    buff.seek(0)
    return buff
