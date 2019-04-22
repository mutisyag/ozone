from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Load initial data"

    FIXTURES = (
        'regions',
        'subregions',
        'parties',
        'meetings',
        'treaties',
        'annexes',
        'groups',
        'substances',
        'substances_edw',
        'blends',
        'blend_components',
        'languages',
        'obligations',
        'reportingperiods',
        'partytypes',
        'partieshistory',
        'partiesratification',
        'reporting_channels',
        'submission_formats',
        'baseline_types',
        'control_measures',
        'baselines',
        'limits',
    )

    FIXTURES_NOT_IN_TEST = (
        'limits',
    )

    def add_arguments(self, parser):
        parser.add_argument("--test", default=False, action="store_true",
                            help="Load test fixtures instead of the normal fixtures.")

    def handle(self, *args, **options):
        for fixture in self.FIXTURES:
            if options["test"] and fixture in self.FIXTURES_NOT_IN_TEST:
                continue
            print("Loading", fixture)
            call_command('loaddata', fixture)
