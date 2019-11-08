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
            table_data = data.get_table_data(
                party, period, submission, all_groups
            )
            # Can be None for inactive parties / no history (e.g. Yugoslavia)
            if table_data:
                yield from render.get_table(table_data)

        yield from render.get_footer()
