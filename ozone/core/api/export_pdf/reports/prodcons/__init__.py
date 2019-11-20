from django.utils.translation import gettext_lazy as _

from . import render
from . import data


def get_prodcons_flowables(submission, periods, parties):
    all_groups = data.get_all_groups()
    groups_description = list(render.get_groups_description(all_groups))

    parties = [submission.party] if submission else parties
    periods = [submission.reporting_period] if submission else periods

    for party in parties:
        yield from render.get_header(party.name)
        yield from groups_description

        for period in periods:
            yield from data.submission_table(party, period, submission, all_groups)

        yield from render.get_footer()


def get_prodcons_by_region_flowables(periods):
    groups_description = list(render.get_groups_description(data.get_all_groups()))

    for period in periods:
        yield from render.get_summary_report_header(period, _("Summary by region"))
        yield from groups_description
        yield data.SummaryByRegion(period).render_table()
        yield render.PageBreak()


def get_prodcons_a5_summary_flowables(periods):
    groups_description = list(render.get_groups_description(data.get_all_groups()))

    for period in periods:
        yield from render.get_summary_report_header(period, _("Summary for All Parties"))
        yield from groups_description
        yield data.SummaryByArt5(period).render_table()
        yield render.PageBreak()


def get_prodcons_parties_flowables(periods, is_article5):
    groups_description = list(render.get_groups_description(data.get_all_groups()))

    for period in periods:
        if is_article5:
            title = _("Article 5 parties")
        else:
            title = _("Non-Article 5 parties")
        yield from render.get_summary_report_header(period, title)
        yield from groups_description
        yield data.SummaryParties(period, is_article5).render_table()
        yield render.PageBreak()
