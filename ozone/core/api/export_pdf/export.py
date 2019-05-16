from io import BytesIO

from reportlab.platypus import SimpleDocTemplate
from reportlab.lib import pagesizes

from . import art7
from . import hat


PG_SIZE = pagesizes.landscape(pagesizes.A4)


def export_submission(submission):
    buff = BytesIO()

    doc = SimpleDocTemplate(
        buff,
        pagesize=PG_SIZE,
        leftMargin=20,
        rightMargin=20,
        topMargin=10,
        bottomMargin=10,
    )
    # TODO: add front page, extra information (country, year?)

    obligation = submission.obligation.form_type
    if obligation == 'art7':
        doc.build(art7.export_submission(submission))
    elif obligation == 'hat':
        doc.build(hat.export_submission(submission))

    buff.seek(0)
    return buff
