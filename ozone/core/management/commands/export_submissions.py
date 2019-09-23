import logging
from django.core.management.base import BaseCommand
from ozone.core.models import Submission
from ozone.core.export.submissions import export_submissions

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('path', help="Path to output excel file")
        parser.add_argument('--party', help="Filter by party")
        parser.add_argument('--period', help="Filter by reporting period")
        parser.add_argument('--limit', type=int,
                            help="Limit number of output rows")

    def handle(self, *args, **options):
        path = options['path']
        party = options.get('party')
        period = options.get('period')
        limit = options.get('limit')

        queryset = Submission.objects.all()
        if party:
            queryset = queryset.filter(party__abbr=party)
        if period:
            queryset = queryset.filter(reporting_period__name=period)
        if limit:
            queryset = queryset[:limit]

        out = export_submissions(queryset)
        out.dump_xlsx(path)
        log.info(f"Successfully generated {path}")
