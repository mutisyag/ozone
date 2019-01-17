from ..constants import TABLE_BLENDS_COMP_HEADER
from ..constants import TABLE_BLENDS_COMP_STYLE
from ..constants import TABLE_BLENDS_COMP_WIDTHS
from ..util import page_title_section
from ..util import STYLES
from .imp_exp_helper import big_table_row
from .imp_exp_helper import component_row
from .imp_exp_helper import table_from_data

from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer
from reportlab.platypus import Table
from reportlab.lib.units import mm

from django.utils.translation import gettext_lazy as _
from functools import partial


def mk_table_substances(submission):
    # Excluding items with no substance,
    # then getting the ones that are not a blend
    imports = submission.article7imports.exclude(substance=None)
    row = partial(big_table_row, isBlend=False)
    return map(row, imports.filter(blend_item=None))

def mk_table_blends(submission):
    imports = submission.article7imports.filter(substance=None)
    row = partial(big_table_row, isBlend=True)
    blends = []

    for blend_row in map(row, imports):

        # Getting the blend object based on the id
        blend = imports.filter(blend__blend_id=blend_row[1]).first()
        row_comp = partial(component_row, blend=blend)
        data = tuple(map(row_comp, blend.blend.components.all()))

        blends.append(blend_row)
        blends.append(
            (
                (Spacer(7, mm),
                 Table(
                    TABLE_BLENDS_COMP_HEADER + data,
                    style=TABLE_BLENDS_COMP_STYLE,
                    colWidths=TABLE_BLENDS_COMP_WIDTHS,
                 ),
                 Spacer(7, mm))
            ,)
        )

    return blends

def export_imports(submission):
    table_substances = tuple(mk_table_substances(submission))
    table_blends = tuple(mk_table_blends(submission))

    imports_page = (
        Paragraph(_('1.1 Substances'), STYLES['Heading2']),
        table_from_data(table_substances, isBlend=False, type='import'),
        PageBreak(),
        Paragraph(_('1.2 Blends'), STYLES['Heading2']),
        table_from_data(table_blends, isBlend=True, type='import'),
        PageBreak(),
    )

    return page_title_section(
        title=_('IMPORTS'),
        explanatory= _(
            'Annexes A, B, C and E substances in metric tonnes (not ODP tonnes)'
        )
    ) + imports_page
