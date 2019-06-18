from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.contrib.postgres.fields import ArrayField


from .reporting import Submission


__all__ = [
    'Email',
    'EmailTemplate',
]


class Email(models.Model):
    subject = models.CharField(max_length=255, blank=True, null=True)
    from_email = models.CharField(max_length=255)
    to = ArrayField(models.CharField(max_length=255))
    cc = ArrayField(models.CharField(max_length=255, blank=True), null=True)
    body = models.TextField(blank=True, null=True)
    submission = models.ForeignKey(
        Submission, related_name='emails', on_delete=models.PROTECT
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


class EmailTemplate(models.Model):
    name = models.CharField(max_length=256)
    subject = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
