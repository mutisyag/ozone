import logging

from django.core.management.base import BaseCommand

from ozone.core.models import Submission, ProdCons

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            default=False,
            help="Use to re-populate all data, otherwise just dry-run"
        )

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
                f"Run with --confirm to process {Submission.objects.count()} "
                f"submissions, delete {ProdCons.objects.count()} aggregations "
                f"and create from scratch around "
                f"{9*Submission.objects.count()} aggregations."
            )
        else:
            ProdCons.objects.all().delete()

        for s in Submission.objects.all():
            if options['confirm']:
                logger.info(f"Aggregating data for submission {s.id}")
            else:
                logger.debug(f"Found submission {s.id}")

            if options['confirm']:
                s.fill_aggregated_data()
