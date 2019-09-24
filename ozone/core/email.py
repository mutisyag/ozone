from django.core.mail import EmailMultiAlternatives
from django.template import loader


def send_mail_from_template(
    subject_template_name,
    email_template_name,
    context,
    to_emails,
    cc_emails=None,
    from_email=None,
    html_email_template_name=None,
):
    """
    Send a django.core.mail.EmailMultiAlternatives to `to_emails`.
    """
    subject = loader.render_to_string(subject_template_name, context)
    subject = "".join(subject.splitlines())
    body = loader.render_to_string(email_template_name, context)

    email_message = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=from_email,
        to=to_emails,
        cc=cc_emails,
    )

    if html_email_template_name is not None:
        html_email = loader.render_to_string(html_email_template_name, context)
        email_message.attach_alternative(html_email, "text/html")

    email_message.send()
