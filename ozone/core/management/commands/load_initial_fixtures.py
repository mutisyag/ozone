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
        'other_submission_types',
    )

    def handle(self, *args, **options):
        for fixture in Command.FIXTURES:
            call_command('loaddata', fixture)
