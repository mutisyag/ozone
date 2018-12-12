"""Deletes all submissions and related data (to be used only during development/testing)
"""
import logging

from django.core.management.base import BaseCommand

from ozone.core.models.reporting import Submission


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = __doc__

    def handle(self, *args, **options):
        stream = logging.StreamHandler()
        stream.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s'
        ))
        logger.addHandler(stream)
        logger.setLevel(logging.INFO)

        if int(options['verbosity']) > 1:
            logger.setLevel(logging.DEBUG)

        def force_allow_delete(self):
            return True

        for s in Submission.objects.all():
            logger.info("Deleting submission %s", s.id)
            for related_data in s.RELATED_DATA:
                for instance in getattr(s, related_data).all():
                    instance.delete()
            s.__class__.data_changes_allowed = force_allow_delete
            s.delete()
