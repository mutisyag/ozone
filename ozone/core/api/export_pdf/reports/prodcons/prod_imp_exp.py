from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph

from ozone.core.api.export_pdf.util import h2_style
from ozone.core.api.export_pdf.util import DOUBLE_HEADER_TABLE_STYLES
from ozone.core.api.export_pdf.util import col_widths
from ozone.core.api.export_pdf.util import TableBuilder

from . import data
from . import render


TABLE_CUSTOM_STYLES = (
    ('SPAN', (0, 0), (0, 1)),  # blank
    ('SPAN', (1, 0), (3, 0)),  # production
    ('SPAN', (4, 0), (6, 0)),  # imports
    ('SPAN', (7, 0), (9, 0)),  # exports
    # ('ALIGN', (1, 2), (-1, -1), 'RIGHT'),
)

class ProdImpExpTable:

    def __init__(self, period):
        self.period = period
        styles = list(DOUBLE_HEADER_TABLE_STYLES + TABLE_CUSTOM_STYLES)
        column_widths = col_widths([6, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5])
        self.builder = TableBuilder(styles, column_widths)
        self.builder.add_row([
            "",
            "PRODUCTION", "", "",
            "IMPORTS", "", "",
            "EXPORTS", "", "",
        ])
        self.builder.add_row([
            "",
            self.period.name, "Base", "% Chng",
            self.period.name, "Base", "% Chng",
            self.period.name, "Base", "% Chng",
        ])

    def done(self):
        return self.builder.done()


def render_header(period):
    title = (
        f"Production, Import and Export of ODSs - "
        f"Comparison of {period.name} with Base (ODP Tons)"
    )
    return Paragraph(title, style=h2_style)


def get_prod_imp_exp_flowables(periods):
    all_groups = data.get_all_groups()
    groups_description = list(render.get_groups_description(all_groups))

    for period in periods:
        yield render_header(period)
        yield from groups_description

        table = ProdImpExpTable(period)
        yield table.done()

        yield PageBreak()
