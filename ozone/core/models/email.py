from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.contrib.postgres.fields import ArrayField


from .reporting import Submission


__all__ = [
    'Email',
    'EmailTemplate',
    'EmailTemplateAttachment',
]


class Email(models.Model):
    date = models.DateTimeField(auto_now_add=True, editable=False)
    subject = models.CharField(max_length=255, blank=True, null=True)
    from_email = models.CharField(max_length=255)
    to = ArrayField(models.CharField(max_length=255))
    cc = ArrayField(models.CharField(max_length=255, blank=True), null=True)
    body = models.TextField(blank=True, null=True)
    submission = models.ForeignKey(
        Submission, related_name='emails',
        null=True, on_delete=models.SET_NULL,
    )

    def send_email(self):
        email = EmailMultiAlternatives(
            subject=self.subject,
            body=self.body,
            from_email=self.from_email,
            to=self.to,
            cc=self.cc
        )
        email.send()

    def __str__(self):
        return f"Email for {self.submission}"


class EmailTemplate(models.Model):
    name = models.CharField(max_length=256)
    subject = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class EmailTemplateAttachment(models.Model):
    email_template = models.ForeignKey(
        EmailTemplate, related_name='attachments',
        on_delete=models.CASCADE,
    )
    file = models.FileField(upload_to='email-template-attachments/')
    filename = models.CharField(max_length=255)

    def __str__(self):
        return self.filename
