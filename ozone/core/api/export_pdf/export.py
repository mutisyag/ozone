from io import BytesIO
from functools import partial
from django.utils.translation import gettext_lazy as _

from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph
from reportlab.lib import pagesizes
from reportlab.lib.units import cm

from . import art7
from . import hat
from . import reports
from .util import right_paragraph_style, left_paragraph_style


def add_page_footer(canvas, doc, footnote=None):
    canvas.saveState()
    if footnote:
        footer = Paragraph(footnote, left_paragraph_style)
        w, h = footer.wrap(doc.width, doc.bottomMargin)
        footer.drawOn(canvas, doc.rightMargin, h/2)

    footer = Paragraph('%s %d' % (_('Page'), canvas._pageNumber), right_paragraph_style)
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.rightMargin, h)

    canvas.restoreState()


add_page_footnotes = partial(
    add_page_footer,
    footnote=_("""* Population in thousands <br/>
    ** Consumption and Production numbers are rounded to a uniform number of decimal places. <br/><br/>
    - = Data Not Reported and Party has no Obligation to have Reported that data at this time. <br/>
    N.R. = Data Not Reported but Party is required to have reported | 
    DIV0 = Division was not evaluated due to a zero or negative base.
    AFR = Africa | 
    ASIA = Asia | 
    EEUR = Eastern Europe | 
    LAC = Latin America & the Caribbean | 
    WEUR = Western Europe & others
    A5 = Article 5 Party | 
    CEIT = Country with Economy in Transition | 
    EU = Member of the European Union | 
    Non-A5 = Non-Article 5 Party""")
)


def export_submissions(submissions):
    buff = BytesIO()

    doc = SimpleDocTemplate(
        buff,
        pagesize=pagesizes.landscape(pagesizes.A4),
        leftMargin=1*cm,
        rightMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm,
    )
    # A4 size is 21cm x 29.7cm
    flowables = [Paragraph('No data', left_paragraph_style)]
    if submissions:
        obligation = submissions[0].obligation.form_type
        if obligation == 'art7':
            flowables = art7.export_submissions(submissions)
    doc.build(
        flowables,
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer,
    )
    buff.seek(0)
    return buff


def export_prodcons(reporting_period, parties):
    buff = BytesIO()

    doc = SimpleDocTemplate(
        buff,
        pagesize=pagesizes.A4,
        leftMargin=0.8*cm,
        rightMargin=0.8*cm,
        topMargin=1*cm,
        bottomMargin=1*cm,
    )

    doc.build(
        reports.export_prodcons(reporting_period, parties),
        onFirstPage=add_page_footnotes,
        onLaterPages=add_page_footnotes
        )

    buff.seek(0)
    return buff
