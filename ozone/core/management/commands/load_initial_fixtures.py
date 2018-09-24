from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Load initial data"

    FIXTURES = ('regions',
                'subregions',
                'parties',
                'meetings',
                'treaties',
                'annexes',
                'groups',
                'substances',
                'languages',
                )

    def handle(self, *args, **options):
        for fixture in Command.FIXTURES:
            call_command('loaddata', fixture)
