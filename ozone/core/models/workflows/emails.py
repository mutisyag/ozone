import re
from ozone.core.models import User
from ozone.core.email import send_mail_from_template
from ozone.core.utils.site import get_site_name


def skip(email):
    if re.search(r'@example\.(com|org)$', email):
        return True


def notify_workflow_transitioned(workflow):
    submission = workflow.model_instance
    context = {
        'user': str(workflow.user),
        'new_state': str(workflow.state).upper(),
        'submission': str(submission),
        'party': submission.party.name,
        'obligation': submission.obligation.name,
        'reporting_period': submission.reporting_period.name,
        'version': str(submission.version),
        'site_name': get_site_name(),
    }

    recipients = [u.email for u in User.objects.filter(is_secretariat=True)]
    recipients.append(submission.info.email)

    for to_email in recipients:
        if skip(to_email):
            continue

        send_mail_from_template(
            "registration/workflow_transitioned_subject.txt",
            "registration/workflow_transitioned_email.html",
            context=context,
            to_email=to_email,
        )
