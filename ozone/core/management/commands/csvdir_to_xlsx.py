from pathlib import Path
from django.core.management.base import BaseCommand
from ozone.core.utils.spreadsheet import OzoneSpreadsheet


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('csvdir', type=Path, help="Input csvdir")
        parser.add_argument('xlsx', type=Path, help="Output excel file")

    def handle(self, *args, **options):
        s = OzoneSpreadsheet.from_csvdir(options['csvdir'])
        s.dump_xlsx(options['xlsx'])
