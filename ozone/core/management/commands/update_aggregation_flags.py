import logging

from django.core.management.base import BaseCommand

from ozone.core.models import ProdCons, ProdConsMT, PartyHistory


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Populates is_eu_member and is_article5 flags for existing ProdCons
    and ProdConsMT entries.
    """

    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            '--odp',
            action='store_true',
            default=False,
            help="Use to populate flags for all ODP aggregations"
        )
        parser.add_argument(
            '--mt',
            action='store_true',
            default=False,
            help="Use to populate flags for all MT aggregations"
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

        if options['odp'] is False and options['mt'] is False:
            logger.info(
                'No action will be performed, run with --odp, --mt or both to '
                'populate flags for ODP and/or MT aggregations'
            )

        updated_odp = 0
        updated_mt = 0

        for ph in PartyHistory.objects.all():
            if options['odp'] is True:
                qs = ProdCons.objects.filter(
                    party=ph.party, reporting_period=ph.reporting_period
                )
                updated_odp += qs.update(
                    is_article5=ph.is_article5, is_eu_member=ph.is_eu_member
                )
            if options['mt'] is True:
                qs = ProdConsMT.objects.filter(
                    party=ph.party, reporting_period=ph.reporting_period
                )
                updated_mt += qs.update(
                    is_article5=ph.is_article5, is_eu_member=ph.is_eu_member
                )

        logger.info(
            f'Updated {updated_odp} ProdCons and {updated_mt} ProdConsMT objects'
        )
