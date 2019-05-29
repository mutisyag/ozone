from django.db import models

from .reporting import Submission


class Email(models.Model):
    subject = models.CharField(max_length=255, blank=True, null=True)
    from_email = models.CharField(max_length=255)
    to = models.CharField(max_length=255)
    cc = models.TextField(blank=True, null=True)
    body_html = models.TextField(blank=True, null=True)
    body_plain = models.TextField(blank=True, null=True)
    submission = models.ForeignKey(
        Submission, related_name='emails', on_delete=models.PROTECT
    )
