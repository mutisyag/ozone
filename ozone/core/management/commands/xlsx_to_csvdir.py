from pathlib import Path
from django.core.management.base import BaseCommand
from ozone.core.utils.spreadsheet import OzoneSpreadsheet


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('xlsx', type=Path, help="Input excel file")
        parser.add_argument('csvdir', type=Path, help="Output csvdir")

    def handle(self, *args, **options):
        s = OzoneSpreadsheet.from_xlsx(options['xlsx'])
        s.dump_csvdir(options['csvdir'])
