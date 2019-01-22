"""Quick fix for staging where reporting channel has been lost for all submission.
Adds reporting channel 'Web form' to all submissions that don't have a
a reporting channel and submissions are all in data entry.
"""

from django.core.management.base import BaseCommand

from ozone.core.models.reporting import Submission, ReportingChannel


class Command(BaseCommand):
    help = __doc__

    def handle(self, *args, **options):
        submissions = Submission.objects.filter(
            reporting_channel__isnull=True,
            _current_state='data_entry'
        )
        for submission in submissions:
            submission.reporting_channel = ReportingChannel.objects.get(name='Web form')
            submission.save()
