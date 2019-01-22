from io import BytesIO

from reportlab.platypus import SimpleDocTemplate
from reportlab.lib import pagesizes

from . import art7
from . import hat


PG_SIZE = pagesizes.landscape(pagesizes.A4)


def export_submission(submission):
    buff = BytesIO()

    doc = SimpleDocTemplate(buff, pagesize=PG_SIZE)
    # TODO: add front page, extra information (country, year?)

    obligation = submission.obligation.name
    if obligation == 'Article 7':
        doc.build(art7.export_submission(submission))
    elif obligation == 'HAT Imports and Production':
        doc.build(hat.export_submission(submission))

    buff.seek(0)
    return buff
