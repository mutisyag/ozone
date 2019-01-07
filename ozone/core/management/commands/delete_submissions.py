"""Deletes all submissions and related data (to be used only during development/testing)
"""
import logging

from django.core.management.base import BaseCommand

from ozone.core.models.reporting import Submission


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('--confirm', action='store_true', default=False,
                            help="Use to really delete all submissions, otherwise just dry-run")

    def handle(self, *args, **options):
        stream = logging.StreamHandler()
        stream.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s'
        ))
        logger.addHandler(stream)
        logger.setLevel(logging.INFO)

        if int(options['verbosity']) > 1:
            logger.setLevel(logging.DEBUG)

        if not options['confirm']:
            logger.info(
                "Run with --confirm to really delete %s submissions.", Submission.objects.count())

        def force_allow_delete(self):
            return True

        for s in Submission.objects.all():
            if options['confirm']:
                logger.info("Deleting submission %s", s.id)
            else:
                logger.debug("Found submission %s", s.id)
            for related_data in s.RELATED_DATA:
                for instance in getattr(s, related_data).all():
                    if options['confirm']:
                        instance.delete()
                    else:
                        logger.debug("Found related data: s", instance)
            s.__class__.data_changes_allowed = force_allow_delete
            if options['confirm']:
                if s.info:
                    s.info.delete()
                s.delete()
