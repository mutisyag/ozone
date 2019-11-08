from decimal import Decimal

from django.utils.translation import gettext_lazy as _
from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph
from reportlab.platypus import Table

from ozone.core.api.export_pdf.util import (
    h1_style, h2_style, sm_no_spacing_style,
    smb_l, sm_l, b_l,
    format_decimal,
    DOUBLE_HEADER_TABLE_STYLES,
    col_widths,
)

TABLE_CUSTOM_STYLES = (
    ('ALIGN', (1, 2), (-1, -1), 'RIGHT'),
    ('SPAN', (0, 0), (0, 1)),  # annex/group
    ('SPAN', (1, 0), (4, 0)),  # production
    ('SPAN', (5, 0), (9, 0)),  # consumption
)


def get_header(party_name):
    return (
        Paragraph(party_name.upper(), style=h1_style),
        Paragraph("Production and Consumption - Comparison with Base Year", style=h2_style),
    )


def get_groups_description(all_groups):
    for group in all_groups:
        yield Paragraph(
            f"{group.group_id} - {group.name_alt} "
            f"{group.description}. {group.description_alt}",
            sm_no_spacing_style
        )

    yield Paragraph("", style=h1_style)


class TableBuilder:

    def __init__(self, styles, column_widths):
        self.styles = list(styles)
        self.column_widths = column_widths
        self.rows = []

    def add_row(self, row):
        self.rows.append(row)

    def add_heading(self, text):
        self.rows.append([smb_l(text)])
        current_row = len(self.rows) - 1
        self.styles.append(('SPAN', (0, current_row), (-1, current_row)))

    def done(self):
        return Table(
            self.rows,
            colWidths=self.column_widths,
            style=self.styles,
            hAlign='LEFT'
        )


def get_party_history(party_data):
    info = _("""{party_name} - Date Reported: {date_reported}
                {party_type} {party_region} - Population*: {population}""".format(
             party_name=party_data['name'],
             date_reported=party_data['date_reported'],
             party_type=party_data['party_type'],
             party_region=party_data['region'],
             population=party_data['population']))
    paragraph = b_l(info)
    paragraph.keepWithNext = True
    return paragraph


def get_table(table_data):
    ods_caption = _("Production and Consumption of ODSs for {period} (ODP tonnes)")
    hfc_caption = _("Production and Consumption of HFCs for {period} (CO2-equivalent tonnes)")

    styles = list(DOUBLE_HEADER_TABLE_STYLES + TABLE_CUSTOM_STYLES)
    column_widths = col_widths([5.5, 1.5, 1.5, 1.2, 1.5, 1.5, 1.5, 1.2, 1.5, 2])
    table_builder = TableBuilder(styles, column_widths)

    period = table_data['period']

    table_builder.add_row([
        _('Annex/Group'),
        "{label}**".format(label=_('PRODUCTION')), '', '', '',
        "{label}**".format(label=_('CONSUMPTION')), '', '', '', '',
    ])
    table_builder.add_row([
        '',
        period, _('Base'), _('% Chng'), _('Limit'),
        period, _('Base'), _('% Chng'), _('Limit'), _('Per Cap. Cons.'),
    ])

    table_builder.add_heading(ods_caption.format(period=period))

    def _format(row):
        return (
            format_decimal(value) if isinstance(value, Decimal) else value
            for value in row
        )

    for k, row in table_data['data'].items():
        if k == 'F':
            continue
        table_builder.add_row(_format(row))

    if 'F' in table_data['data']:
        row = table_data['data']['F']
        table_builder.add_heading(hfc_caption.format(period=period))
        table_builder.add_row(_format(row))

    yield get_party_history(table_data['party'])
    yield table_builder.done()
    yield Paragraph('', style=h1_style)


def get_footer():
    yield sm_l(_(
        """* Population in thousands <br/>
        ** Consumption and Production numbers are rounded to a uniform number of decimal places. <br/><br/>
        - = Data Not Reported and Party has no Obligation to have Reported that data at this time. <br/>
        N.R. = Data Not Reported but Party is required to have reported |
        AFR = Africa |
        ASIA = Asia |
        EEUR = Eastern Europe |
        LAC = Latin America & the Caribbean |
        WEUR = Western Europe & others |
        A5 = Article 5 Party |
        NA5 = Non-Article 5 Party"""
    ))
    yield PageBreak()
