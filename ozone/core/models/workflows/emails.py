import re
from ozone.core.models import User
from ozone.core.email import send_mail_from_template
from ozone.core.utils.site import get_site_name


def allow_sending_to(email):
    # if re.search(r'@example\.(com|org)$', email):
    #     return False

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
