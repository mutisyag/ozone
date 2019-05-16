from ..util import get_comments_section
from ..util import p_l, p_c
from ..util import h1_style
from .constants import TABLE_INFO_WIDTHS, TABLE_INFO_HEADER, TABLE_INFO_STYLE

from django.utils.translation import gettext_lazy as _
from reportlab.platypus import Paragraph
from reportlab.platypus import Table


def get_date_of_reporting(submission):
    date_of_reporting = submission.submitted_at or submission.info.date
    if not date_of_reporting:
        return None
    else:
        return (
            p_l('%s: %s' % (
                _('Date of reporting'),
                date_of_reporting.strftime('%-d %B %Y'),
            )),
        )


def _kv(obj, label, prop):
    if not hasattr(obj, prop) or not getattr(obj, prop):
        return None
    return p_l('%s: %s' % (_(label), getattr(obj, prop)))


def get_submission_info(info):
    return (
        _kv(info, 'Name of reporting officer', 'reporting_officer'),
        _kv(info, 'Designation', 'designation'),
        _kv(info, 'Organization', 'organization'),
        _kv(info, 'Postal address', 'postal_address'),
        _kv(info, 'Address country', 'country'),
        _kv(info, 'Phone', 'phone'),
        _kv(info, 'E-mail', 'email'),
    )


def get_questionnaire_table(submission):
    def _yn(condition):
        return p_c(_('Yes') if condition else _('No'))
    row = (
        _yn(submission.article7questionnaire.has_imports),
        _yn(submission.article7questionnaire.has_exports),
        _yn(submission.article7questionnaire.has_produced),
        _yn(submission.article7questionnaire.has_destroyed),
        _yn(submission.article7questionnaire.has_nonparty),
        _yn(submission.article7questionnaire.has_emissions),

        _yn(submission.flag_has_reported_a1),
        _yn(submission.flag_has_reported_a2),
        _yn(submission.flag_has_reported_b1),
        _yn(submission.flag_has_reported_b2),
        _yn(submission.flag_has_reported_b3),
        _yn(submission.flag_has_reported_c1),
        _yn(submission.flag_has_reported_c2),
        _yn(submission.flag_has_reported_c3),
        _yn(submission.flag_has_reported_e),
        _yn(submission.flag_has_reported_f),
    )
    return (
        Table(
                TABLE_INFO_HEADER + (row,),
                colWidths=TABLE_INFO_WIDTHS,
                style=TABLE_INFO_STYLE,
                hAlign='LEFT',
        ),
    )


def export_info(submission):
    return (
        Paragraph("%s %s - %s" % (
            submission.reporting_period.name,
            submission.obligation.name,
            submission.party.name,
        ), h1_style),
    ) + get_date_of_reporting(submission)
    + get_submission_info(submission.info)
    + get_questionnaire_table(submission)
    + get_comments_section(submission, 'questionnaire')
