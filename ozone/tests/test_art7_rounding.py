import decimal

from pathlib import Path
from datetime import datetime
from django.contrib.auth.hashers import Argon2PasswordHasher
from django.core.management import call_command

from ozone.core.models import (
    Article7Import,
    Article7Production,
    Article7NonPartyTrade,
)

from .base import BaseTests
from . import factories

examples = Path(__file__).resolve().parent / 'examples'


class RoundingTest(BaseTests):

    def setUp(self):
        super().setUp()
        self.language = factories.LanguageEnFactory()
        hash_alg = Argon2PasswordHasher()
        self.secretariat_user = factories.SecretariatUserFactory(
            language=self.language,
            password=hash_alg.encode(password="qwe123qwe", salt="123salt123"),
        )

        subregion = factories.SubregionFactory()

        parties = ['TP', 'NPA', 'NPB']
        for party in parties:
            factories.PartyFactory(
                abbr=party,
                name=f"{party} party",
                subregion=subregion,
            )

        factories.ReportingPeriodFactory(
            name='2000',
            start_date=datetime.strptime('2000-01-01', '%Y-%m-%d'),
            end_date=datetime.strptime('2000-12-31', '%Y-%m-%d'),
        )
        factories.ReportingChannelFactory(name="Legacy")
        substances = [100, 101, 102, 103, 104, 105, 106, 999]
        for substance_id in substances:
            factories.SubstanceFactory(
                substance_id=substance_id,
                name=f"Chemical {substance_id}",
            )

        factories.ObligationFactory(pk=1)

    def test_rounding(self):
        in_path = examples / 'art7_rounding_issues.xlsx'
        call_command('import_submissions', in_path)

        assert 1 == Article7Import.objects.count()
        assert 1 == Article7Production.objects.count()

        imp = Article7Import.objects.get(substance__substance_id=100)
        assert imp.quantity_essential_uses == decimal.Decimal('0.00009')
        assert imp.quantity_laboratory_analytical_uses == decimal.Decimal('0.469')

        prod = Article7Production.objects.get(substance__substance_id=100)
        assert prod.quantity_essential_uses == decimal.Decimal('4.34890')
        assert prod.quantity_laboratory_analytical_uses == decimal.Decimal('0.00135')
        assert prod.quantity_total_produced == decimal.Decimal('4.35025')

        npt = Article7NonPartyTrade.objects.get(
            substance__substance_id=100,
            trade_party__abbr='NPA',
        )
        assert npt.quantity_import_new == decimal.Decimal('0.00004')
        assert npt.quantity_import_recovered == decimal.Decimal('0.000037')
        npt = Article7NonPartyTrade.objects.get(
            substance__substance_id=100,
            trade_party__abbr='NPB',
        )
        assert npt.quantity_export_new == decimal.Decimal('0.00001')
        assert npt.quantity_export_recovered == decimal.Decimal('0.00079')
