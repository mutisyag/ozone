import logging

from django.core.management.base import BaseCommand

from ozone.core.models import (
    ProdConsMT,
    Party,
    ReportingPeriod,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Re-calculates and saves the calculated fields for all MT aggregations.
    """

    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            '--party',
            help="Party code (abbreviation), for limiting the calculation to a "
                 "single party."
        )
        parser.add_argument(
            '--period',
            help="Reporting period code, for limiting the calculation to a "
                 "single reporting period."
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            default=False,
            help="Use to re-calculate all data, otherwise just dry-run"
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

        prodcons_mt_queryset = ProdConsMT.objects.all()
        if options['party']:
            party = Party.objects.get(abbr=options['party'])
            prodcons_mt_queryset = prodcons_mt_queryset.filter(party=party)

        if options['period']:
            period = ReportingPeriod.objects.get(name=options['period'])
            prodcons_mt_queryset = prodcons_mt_queryset.filter(
                reporting_period=period
            )

        if not options['confirm']:
            logger.info(
                f"Run with --confirm to process and update "
                f"{prodcons_mt_queryset.count()} existing MT aggregations."
            )

        for a in prodcons_mt_queryset:
            if options['confirm']:
                logger.info(f"Recalculating data for {a}")
                # This triggers a recalculation of the totals
                a.save()
            else:
                logger.debug(f"Found aggregation {a.id}")
