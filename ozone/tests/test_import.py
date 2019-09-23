from decimal import Decimal as D
from pathlib import Path
from django.contrib.auth.hashers import Argon2PasswordHasher
from ozone.core.management.commands import import_submissions
from ozone.core.utils.spreadsheet import OzoneSpreadsheet
from ozone.core import models
from .base import BaseTests
from . import factories
from .fixtures_for_importing import get_required_fixtures
from .fixtures_for_importing import create_fixtures

examples = Path(__file__).resolve().parent / 'examples'


def invoke_import_submissions(**kwargs):
    kwargs = dict({
        'recreate': False,
        'purge': False,
        'limit': None,
        'precision': 10,
        'use_cache': False,
        'dry_run': False,
        'single': False,
        'verbosity': 1,
    }, **kwargs)
    cmd = import_submissions.Command()
    cmd.handle(**kwargs)


class ImportTest(BaseTests):

    def setUp(self):
        super().setUp()
        self.language = factories.LanguageEnFactory()
        hash_alg = Argon2PasswordHasher()
        self.secretariat_user = factories.SecretariatUserFactory(
            language=self.language,
            password=hash_alg.encode(password="qwe123qwe", salt="123salt123"),
        )
        self.subregion = factories.SubregionFactory()
        factories.ReportingChannelFactory(name="Legacy")
        factories.ObligationFactory(pk=1)

    def test_blend_is_expanded_into_components(self):
        in_path = examples / 'art7_submissions.xlsx'
        in_data = OzoneSpreadsheet.from_xlsx(in_path)
        blend_list = [
            (369, [
                (101, D('0.3')),
                (102, D('0.7')),
            ]),
        ]
        fixtures = get_required_fixtures(in_data, blend_list=blend_list)
        create_fixtures(self.subregion, **fixtures)
        invoke_import_submissions(file=in_path)

        s101 = models.Substance.objects.get(substance_id='101')
        s102 = models.Substance.objects.get(substance_id='102')
        [submission] = models.Submission.objects.all()

        import_blends = {
            row.substance: row for row in
            submission.article7imports.filter(blend_item_id__isnull=False)
        }

        assert set(import_blends.keys()) == set([s101, s102])
        assert import_blends[s101].quantity_total_new == D('18')
        assert import_blends[s102].quantity_total_new == D('42')
