from io import BytesIO
from django.utils.translation import gettext_lazy as _

from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph
from reportlab.lib import pagesizes
from reportlab.lib.units import cm

from . import art7

from .reports import (
    prodcons,
    raf,
    impexp_new_rec,
    impexp,
    hfc_baseline,
)

from ozone.core.models import (
    ObligationTypes,
)

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


def export_submissions(obligation, submissions):

    buff, doc = get_doc_template(landscape=True)
    if obligation._obligation_type == ObligationTypes.ART7.value:
        clazz = art7
    elif obligation._obligation_type == ObligationTypes.ESSENCRIT.value:
        clazz = raf

    flowables = (
        list(clazz.export_submissions(submissions)) or
        [Paragraph('No data', left_paragraph_style)]
    )

    doc.build(
        flowables,
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer,
    )
    buff.seek(0)
    return buff


def export_baseline_hfc_raw(parties):
    buff, doc = get_doc_template(landscape=True)
    doc.build(
        list(art7.export_baseline_hfc_raw(parties)),
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer,
    )
    buff.seek(0)
    return buff


def export_labuse(periods):

    buff, doc = get_doc_template(landscape=False)

    flowables = (
        list(art7.export_labuse_report(periods)) or
        [Paragraph('No data', left_paragraph_style)]
    )

    doc.build(
        flowables,
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer,
    )
    buff.seek(0)
    return buff


def export_prodcons(submission, periods, parties):
    buff, doc = get_doc_template(landscape=False)

    doc.build(
        list(prodcons.get_prodcons_flowables(submission, periods, parties)),
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer
    )

    buff.seek(0)
    return buff


def export_prodcons_by_region(periods):
    buff, doc = get_doc_template(landscape=False)

    doc.build(
        list(prodcons.get_prodcons_by_region_flowables(periods)),
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer
    )

    buff.seek(0)
    return buff


def export_prodcons_a5_summary(periods):
    buff, doc = get_doc_template(landscape=False)

    doc.build(
        list(prodcons.get_prodcons_a5_summary_flowables(periods)),
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer
    )

    buff.seek(0)
    return buff


def export_prodcons_parties(periods, is_article5):
    buff, doc = get_doc_template(landscape=False)

    doc.build(
        list(prodcons.get_prodcons_parties_flowables(periods, is_article5)),
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer
    )

    buff.seek(0)
    return buff


def export_impexp_new_rec(periods, parties):
    buff, doc = get_doc_template(landscape=False)

    doc.build(
        list(impexp_new_rec.get_flowables(periods, parties)),
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer
    )

    buff.seek(0)
    return buff


def export_impexp_rec_subst(periods):
    buff, doc = get_doc_template(landscape=False)

    doc.build(
        list(impexp.get_rec_subst_flowables(periods)),
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer
    )

    buff.seek(0)
    return buff


def export_impexp_new_rec_agg(periods):
    buff, doc = get_doc_template(landscape=False)

    doc.build(
        list(impexp.get_impexp_new_rec_agg_flowables(periods)),
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer
    )

    buff.seek(0)
    return buff


def export_hfc_baseline(parties):
    buff, doc = get_doc_template(landscape=False)

    doc.build(
        list(hfc_baseline.get_flowables(parties)),
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer
    )

    buff.seek(0)
    return buff
