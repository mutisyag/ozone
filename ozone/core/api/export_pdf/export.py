from reportlab.platypus import Paragraph

from . import art7

from .reports import (
    prodcons,
    raf,
    impexp_new_rec,
    impexp,
    hfc_baseline,
    baseline_prod_cons,
)
from .reports.prodcons.prod_imp_exp import get_prod_imp_exp_flowables

from ozone.core.models import (
    ObligationTypes,
)

from .util import left_paragraph_style
from .util import add_page_footer
from .util import get_doc_template


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


def export_prod_imp_exp(periods, parties):
    buff, doc = get_doc_template(landscape=False)

    doc.build(
        list(get_prod_imp_exp_flowables(periods, parties)),
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


def export_baseline_prod_a5(parties):
    buff, doc = get_doc_template(landscape=False)

    doc.build(
        list(baseline_prod_cons.get_prod_a5_flowables(parties)),
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer
    )

    buff.seek(0)
    return buff


def export_baseline_cons_a5(parties):
    buff, doc = get_doc_template(landscape=False)

    doc.build(
        list(baseline_prod_cons.get_cons_a5_flowables(parties)),
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer
    )

    buff.seek(0)
    return buff


def export_baseline_prodcons_na5(parties):
    buff, doc = get_doc_template(landscape=False)

    doc.build(
        list(baseline_prod_cons.get_prodcons_na5_flowables(parties)),
        onFirstPage=add_page_footer,
        onLaterPages=add_page_footer
    )

    buff.seek(0)
    return buff
