from io import BytesIO
from functools import partial
from django.utils.translation import gettext_lazy as _

from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph
from reportlab.lib import pagesizes
from reportlab.lib.units import cm

from . import art7
from . import hat

from .reports import prodcons

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


def get_doc_template(landscape=False):
    buff = BytesIO()
    # A4 size is 21cm x 29.7cm
    if landscape:
        doc = SimpleDocTemplate(
            buff,
            pagesize=pagesizes.landscape(pagesizes.A4),
            leftMargin=1*cm,
            rightMargin=1*cm,
            topMargin=1*cm,
            bottomMargin=1*cm,
        )
    else:
        doc = SimpleDocTemplate(
            buff,
            pagesize=pagesizes.A4,
            leftMargin=0.8*cm,
            rightMargin=0.8*cm,
            topMargin=1*cm,
            bottomMargin=1*cm,
        )
    return buff, doc


def export_submissions(submissions):

    buff, doc = get_doc_template(landscape=True)

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


def export_prodcons(submission, periods, parties):
    buff, doc = get_doc_template(landscape=False)

    add_page_footnotes = partial(
        add_page_footer,
        footnote=prodcons.get_footnote()
    )

    doc.build(
        list(prodcons.get_prodcons_flowables(submission, periods, parties)),
        onFirstPage=add_page_footnotes,
        onLaterPages=add_page_footnotes
    )

    buff.seek(0)
    return buff
