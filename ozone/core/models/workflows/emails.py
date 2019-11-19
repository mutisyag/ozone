import re
from django.utils.translation import gettext as _
from ozone.core.models import User
from ozone.core.email import send_mail_from_template
from ozone.core.utils.site import get_site_name


def allow_sending_to(email):
    if re.search(r'@example\.(com|org)$', email):
        return False

    return True


def notify_workflow_transitioned(workflow):
    submission = workflow.model_instance

    secretariat_states = {
        'processing': _('started PROCESSING'),
        'finalized': _('FINALIZED'),
    }
    party_states = {
        'submitted': _('SUBMITTED'),
        'recalled': _('RECALLED'),
    }

    if workflow.state in secretariat_states:
        intro_text = _(
            'The secretariat has {verb} the report from {party} on'.format(
                verb=secretariat_states.get(workflow.state),
                party=submission.party.name,
            )
        )
    else:
        intro_text = _(
            '{party_name} has {verb} its report on'.format(
                party_name=submission.party.name,
                verb=party_states.get(workflow.state),
            )
        )

    if workflow.state == 'submitted' and workflow.user.email != submission.info.email:
        user = submission.info.email
        data_entry_by = _(
            _('(Information recorded by {user})').format(
                user=str(workflow.user)
            )
        )
    else:
        user = str(workflow.user)
        data_entry_by = ''

    context = {
        'user': user,
        'new_state': str(workflow.state).upper(),
        'new_state_verb': str(workflow.state).title(),
        'intro_text': intro_text,
        'data_entry_by': data_entry_by,
        'submission': str(submission),
        'obligation': submission.obligation.name,
        'reporting_period': submission.reporting_period.name,
        'version': str(submission.version),
        'site_name': get_site_name(),
    }

    to_emails = set(u.email for u in User.objects.filter(is_secretariat=True))
    cc_emails = set(u.email for u in submission.party.users.all())
    cc_emails.add(submission.info.email)

    send_mail_from_template(
        "registration/workflow_transitioned_subject.txt",
        "registration/workflow_transitioned_email.html",
        context=context,
        to_emails=filter(allow_sending_to, to_emails),
        cc_emails=filter(allow_sending_to, cc_emails),
    )
