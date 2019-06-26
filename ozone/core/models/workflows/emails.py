import re
from ozone.core.models import User
from ozone.core.email import send_mail_from_template


def skip(email):
    if re.search(r'@example\.(com|org)$', email):
        return True


def notify_workflow_transitioned(workflow):
    submission = workflow.model_instance
    context = {
        'submission': submission,
        'user': workflow.user,
        'new_state': workflow.state,
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
            to_email=recipients,
        )
