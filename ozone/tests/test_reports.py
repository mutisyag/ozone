from datetime import datetime
from django.contrib.auth.hashers import Argon2PasswordHasher

from ozone.core.models import ObligationTypes
from .base import BaseTests
from . import factories


class TestReports(BaseTests):

    def obligation_factory(self, type):
        return factories.ObligationFactory.create(
            name=f"Obligation {type}",
            _obligation_type=type,
        )

    def period_factory(self, year):
        return factories.ReportingPeriodFactory(
            name=f"{year}",
            start_date=datetime.strptime(f"{year}-01-01", "%Y-%m-%d"),
            end_date=datetime.strptime(f"{year}-12-31", "%Y-%m-%d"),
        )

    def group_factory(self, gid):
        return factories.GroupFactory(
            group_id=gid,
            name=f"Fictitious Group {gid}",
            control_treaty=self.treaty,
            report_treaty=self.treaty,
            annex=self.annex,
        )

    def setUp(self):
        language = factories.LanguageEnFactory()
        hash_alg = Argon2PasswordHasher()
        hashpw = hash_alg.encode(password="qwe123qwe", salt="123salt123")
        secretariat = factories.SecretariatUserFactory(language=language, password=hashpw)
        self.client.login(username=secretariat.username, password="qwe123qwe")
        self.art7 = self.obligation_factory(ObligationTypes.ART7.value)
        self.raf = self.obligation_factory(ObligationTypes.ESSENCRIT.value)

        weur = factories.RegionFactory(abbr="WEUR", name="Western Europe and Others")
        unsp = factories.SubregionFactory(region=weur, abbr="UNK", name="Unspecified")
        self.treaty = factories.TreatyFactory()
        self.annex = factories.AnnexFactory()
        self.au = factories.PartyFactory(abbr="AU", name="Australia", subregion=unsp)
        self.p = {year: self.period_factory(year) for year in range(1980, 2020)}
        self.g = {gid: self.group_factory(gid) for gid in ["AI", "CI", "F"]}

    def get_report_defs(self):
        resp = self.client.get("/api/reports/")
        assert resp.status_code == 200
        return {r["name"]: r for r in resp.json()}

    def get_report_pdf(self, name, **kwargs):
        resp = self.client.get(f"/api/reports/{name}/", **kwargs)
        assert resp.status_code == 200
        assert resp["Content-Type"] == "application/pdf"
        pdf = resp.content
        assert pdf.startswith(b"%PDF-")
        return pdf

    def test_art7_raw(self):
        definition = self.get_report_defs()["art7_raw"]
        assert definition["has_party_param"]
        assert definition["has_period_param"]
        self.get_report_pdf("art7_raw", period=self.p[2009].pk, party=self.au.pk)

    def test_baseline_hfc_raw(self):
        definition = self.get_report_defs()["baseline_hfc_raw"]
        assert definition["has_party_param"]
        self.get_report_pdf("baseline_hfc_raw", party=self.au.pk)

    def test_labuse(self):
        definition = self.get_report_defs()["labuse"]
        assert definition["has_period_param"]
        self.get_report_pdf("labuse", period=self.p[2009].pk)

    def test_prodcons(self):
        definition = self.get_report_defs()["prodcons"]
        assert definition["has_party_param"]
        assert definition["has_period_param"]
        self.get_report_pdf("prodcons", period=self.p[2009].pk, party=self.au.pk)

    def test_prodcons_by_region(self):
        definition = self.get_report_defs()["prodcons_by_region"]
        assert definition["has_period_param"]
        self.get_report_pdf("prodcons_by_region", period=self.p[2009].pk)

    def test_prodcons_a5_summary(self):
        definition = self.get_report_defs()["prodcons_a5_summary"]
        assert definition["has_period_param"]
        self.get_report_pdf("prodcons_a5_summary", period=self.p[2009].pk)

    def test_prodcons_a5_parties(self):
        definition = self.get_report_defs()["prodcons_a5_parties"]
        assert definition["has_period_param"]
        self.get_report_pdf("prodcons_a5_parties", period=self.p[2009].pk)

    def test_prodcons_na5_parties(self):
        definition = self.get_report_defs()["prodcons_na5_parties"]
        assert definition["has_period_param"]
        self.get_report_pdf("prodcons_na5_parties", period=self.p[2009].pk)

    def test_raf(self):
        definition = self.get_report_defs()["raf"]
        assert definition["has_party_param"]
        assert definition["has_period_param"]
        self.get_report_pdf("raf", period=self.p[2009].pk, party=self.au.pk)

    def test_impexp_new_rec(self):
        definition = self.get_report_defs()["impexp_new_rec"]
        assert definition["has_party_param"]
        assert definition["has_period_param"]
        self.get_report_pdf("impexp_new_rec", period=self.p[2009].pk, party=self.au.pk)

    def test_prod_imp_exp(self):
        definition = self.get_report_defs()["prod_imp_exp"]
        assert definition["has_party_param"]
        assert definition["has_period_param"]
        self.get_report_pdf("prod_imp_exp", period=self.p[2009].pk, party=self.au.pk)

    def test_impexp_rec_subst(self):
        definition = self.get_report_defs()["impexp_rec_subst"]
        assert definition["has_period_param"]
        self.get_report_pdf("impexp_rec_subst", period=self.p[2009].pk)

    def test_impexp_new_rec_agg(self):
        definition = self.get_report_defs()["impexp_new_rec_agg"]
        assert definition["has_period_param"]
        self.get_report_pdf("impexp_new_rec_agg", period=self.p[2009].pk)

    def test_hfc_baseline(self):
        definition = self.get_report_defs()["hfc_baseline"]
        assert definition["has_party_param"]
        self.get_report_pdf("hfc_baseline", party=self.au.pk)

    def test_baseline_prod_a5(self):
        definition = self.get_report_defs()["baseline_prod_a5"]
        assert definition["has_party_param"]
        self.get_report_pdf("baseline_prod_a5", party=self.au.pk)

    def test_baseline_cons_a5(self):
        definition = self.get_report_defs()["baseline_cons_a5"]
        assert definition["has_party_param"]
        self.get_report_pdf("baseline_cons_a5", party=self.au.pk)

    def test_baseline_prodcons_na5(self):
        definition = self.get_report_defs()["baseline_prodcons_na5"]
        assert definition["has_party_param"]
        self.get_report_pdf("baseline_prodcons_na5", party=self.au.pk)
