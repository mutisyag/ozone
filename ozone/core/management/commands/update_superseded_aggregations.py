import logging

from django.core.management.base import BaseCommand

from ozone.core.models import (
    Submission,
    Party,
    ReportingPeriod,
    ObligationTypes
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Re-calculates aggregations for submissions that have superseded other
    submissions.
    Used to fix situations in which reported groups have changed from one
    submission to the other - which leaves some stale ProdCons objects.
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

        # Find all Art 7 Submissions that were superseded
        superseded_submission_qs = Submission.objects.filter(
            obligation___obligation_type=ObligationTypes.ART7.value,
            flag_superseded=True
        )
        if options['party']:
            party = Party.objects.get(abbr=options['party'])
            superseded_submission_qs = superseded_submission_qs.filter(
                party=party
            )

        if options['period']:
            period = ReportingPeriod.objects.get(name=options['period'])
            superseded_submission_qs = superseded_submission_qs.filter(
                reporting_period=period
            )

        values = superseded_submission_qs.values_list(
            'party', 'reporting_period'
        )
        values = set(values)

        if not options['confirm']:
            logger.info(
                f"Run with --confirm to remove aggregated data from "
                f"{superseded_submission_qs.count()} superseded submissions "
                f"and recalculate the data based on the current ones."
            )

        for s in superseded_submission_qs:
            if options['confirm']:
                logger.info(f"Deleting data for {s}")
                s.purge_aggregated_data(invalidate_cache=False)
            else:
                logger.debug(f"Found superseded submission {s}")

        for party, reporting_period in values:
            current_submission = Submission.objects.filter(
                party=party,
                reporting_period=reporting_period,
                obligation___obligation_type=ObligationTypes.ART7.value,
                flag_superseded=False
            ).first()
            # Do not recalculate based on editable submissions
            if (
                current_submission
                and not current_submission.data_changes_allowed
            ):
                if options['confirm']:
                    logger.info(f"Calculating data for {current_submission}")
                    current_submission.fill_aggregated_data()
                else:
                    logger.debug(
                        f"Found current submission {current_submission}"
                    )
