from io import BytesIO
from django.utils.translation import gettext_lazy as _

from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph
from reportlab.lib import pagesizes
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle

from . import art7
from . import hat
from .util import right_paragraph_style


PG_SIZE = pagesizes.landscape(pagesizes.A4)


def add_page_number(canvas, doc):
    canvas.saveState()

    footer = Paragraph('%s %d' % (_('Page'), canvas._pageNumber), right_paragraph_style)
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.rightMargin, h)

    canvas.restoreState()


def export_submission(submission):
    buff = BytesIO()

    doc = SimpleDocTemplate(
        buff,
        pagesize=PG_SIZE,
        leftMargin=1*cm,
        rightMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm,
    )
    # TODO: add front page, extra information (country, year?)

    obligation = submission.obligation.form_type
    if obligation == 'art7':
        doc.build(
            art7.export_submission(submission),
            onFirstPage=add_page_number,
            onLaterPages=add_page_number,
        )
    elif obligation == 'hat':
        doc.build(hat.export_submission(submission))

    buff.seek(0)
    return buff


def export_prodcons(reporting_period, parties):
    buf = BytesIO()

    doc = SimpleDocTemplate(buf, pagesize=PG_SIZE)
    doc.build(art7.export_prodcons(reporting_period, parties))

    buf.seek(0)
    return buf
