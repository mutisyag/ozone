from ozone.core.models import Baseline
from ozone.core.models import Group
from ozone.core.models import Limit
from ozone.core.models import LimitTypes
from ozone.core.models import ObligationTypes
from ozone.core.models import PartyHistory
from ozone.core.models import ProdCons
from ozone.core.models import Submission
from ozone.core.models.utils import round_decimal_half_up
from ozone.core.api.export_pdf.util import get_date_of_reporting_str


def get_all_groups():
    return Group.objects.all()


def get_limit(party, period, group, limit_type):
    limit = Limit.objects.filter(
        party=party,
        reporting_period=period,
        group=group,
        limit_type=limit_type,
    ).first()
    return limit.limit if limit else None


def get_formatted_limit(limit):
    return limit if limit is not None else '-'


def get_chng(actual_value, baseline):
    if isinstance(actual_value, str):
        return '-'
    elif actual_value <= 0:
        # even when baseline was not reported
        return -100
    elif baseline is None:
        return '-'
    elif actual_value > 0 and baseline != 0:
        return round_decimal_half_up(
            actual_value / baseline * 100 - 100,
            2
        )
    else:
        return -100


def check_skip_group(values):
    return all(
        val is None or val == '-' or val == ""
        for val in values
    )


class ProdConsTable:

    def __init__(self, party, period, history, all_groups):
        self.all_groups = all_groups
        self.party = party
        self.period = period
        self.show_prod = not party.is_eu
        self.show_cons = not history.is_eu_member
        self.is_article5 = history.is_article5
        self.population = history.population

        self.to_report_groups = Group.get_report_groups(party, period)
        self.controlled_groups = Group.get_controlled_groups(party, period)

        self.prodcons_qs = ProdCons.objects.filter(
            party=party,
            reporting_period=period,
        )

    def get_main_prodcons(self, group):
        try:
            return self.prodcons_qs.get(group=group)
        except ProdCons.DoesNotExist:
            return None

    def get_date_reported(self):
        # Get the date reported from the Article 7 submission related to ProdCons
        submission_id = None
        for subs in self.prodcons_qs.values_list('submissions', flat=True):
            id_list = subs.get(ObligationTypes.ART7.value, [])
            if id_list:
                submission_id = id_list[0]
        sub = Submission.objects.filter(id=submission_id).first()
        if sub:
            # There should only be one current submission.
            return get_date_of_reporting_str(sub)
        else:
            return "-"

    def get_per_capita_cons(self, cons):
        if cons is None or isinstance(cons, str) or not self.population:
            return '-'
        else:
            return round_decimal_half_up(cons / self.population, 4)

    def get_formatted_value(self, prodcons, field, group):
        if prodcons and getattr(prodcons, field) is not None:
            actual_value = getattr(prodcons, field)
        else:
            if group in self.to_report_groups:
                actual_value = 'N.R.'
            else:
                actual_value = '-'
        return actual_value

    def get_formatted_baseline(self, baseline, actual, group, limit):
        # actual is get_formatted_value(production/consumption)
        if baseline is None:
            if (
                group not in self.controlled_groups or
                group.group_id in ['CII', 'CIII'] or
                limit is None
            ):
                return '-'
            return 'N.R.'
        else:
            return baseline if actual != '-' else '-'

    def get_table_row(self, group):
        main_prodcons = self.get_main_prodcons(group)

        if main_prodcons:
            # Get some pre-calculated values
            limit_prod = main_prodcons.limit_prod
            limit_cons = main_prodcons.limit_cons
            baseline_prod = main_prodcons.baseline_prod
            baseline_cons = main_prodcons.baseline_cons
        else:
            limit_prod = get_limit(
                self.party,
                self.period,
                group,
                LimitTypes.PRODUCTION.value,
            )
            limit_cons = get_limit(
                self.party,
                self.period,
                group,
                LimitTypes.CONSUMPTION.value,
            )
            baseline_prod = Baseline.objects.filter(
                party=self.party,
                group=group,
                baseline_type__name='A5Prod' if self.is_article5 else 'NA5Prod',
            ).first()
            baseline_prod = baseline_prod.baseline if baseline_prod else None
            baseline_cons = Baseline.objects.filter(
                party=self.party,
                group=group,
                baseline_type__name='A5Cons' if self.is_article5 else 'NA5Cons',
            ).first()
            baseline_cons = baseline_cons.baseline if baseline_cons else None

        if self.show_prod:
            main_prod = self.get_formatted_value(
                main_prodcons,
                'calculated_production',
                group,
            )
        else:
            main_prod = None

        if self.show_cons:
            main_cons = self.get_formatted_value(
                main_prodcons,
                'calculated_consumption',
                group,
            )
        else:
            main_cons = None

        per_capita_cons = self.get_per_capita_cons(
            main_cons
        ) if self.show_cons else None

        # % reduction vs base year
        chng_prod = get_chng(
            main_prod, baseline_prod
        ) if self.show_prod else None

        chng_cons = get_chng(
            main_cons, baseline_cons
        ) if self.show_cons else None

        baseline_prod = self.get_formatted_baseline(
            baseline_prod, main_prod, group, limit_prod
        ) if self.show_prod else None

        baseline_cons = self.get_formatted_baseline(
            baseline_cons, main_cons, group, limit_cons
        ) if self.show_cons else None

        limit_prod = get_formatted_limit(
            limit_prod
        ) if self.show_prod else None

        limit_cons = get_formatted_limit(
            limit_cons
        ) if self.show_cons else None

        skip_group = check_skip_group(
            [main_prod, baseline_prod, main_cons, baseline_cons]
        )

        row = (
            '{id}  - {descr}'.format(
                id=group.group_id,
                descr=group.description
            ),

            main_prod,
            baseline_prod,
            chng_prod,
            limit_prod,

            main_cons,
            baseline_cons,
            chng_cons,
            limit_cons,

            per_capita_cons,
        )

        return (row, skip_group)

    def get_data_rows(self):
        rv = {}

        for group in self.all_groups:
            (row, skip_group) = self.get_table_row(group)

            if not skip_group:
                rv[group.group_id] = row

        return rv


class SubmissionTable(ProdConsTable):

    def __init__(self, submission, history, all_groups):
        self.submission = submission
        party = submission.party
        period = submission.reporting_period
        super().__init__(party, period, history, all_groups)

        # We need to get the actual data from *this* submission
        self.prodcons_data = submission.get_aggregated_data()

    def get_main_prodcons(self, group):
        return self.prodcons_data.get(group, None)

    def get_date_reported(self):
        return get_date_of_reporting_str(self.submission)


def get_table_data(party, period, submission, all_groups):
    try:
        history = PartyHistory.objects.get(
            party=party,
            reporting_period=period
        )
        population = history.population
        party_type = history.party_type.abbr
    except PartyHistory.DoesNotExist:
        return None

    if submission:
        table = SubmissionTable(submission, history, all_groups)
    else:
        table = ProdConsTable(party, period, history, all_groups)

    table_data = {}

    table_data['period'] = period.name

    table_data['party'] = {
        'name': party.name,
        'population': '{:,}'.format(population) if population else '',
        'party_type': party_type,
        'date_reported': table.get_date_reported(),
        'region': party.subregion.region.abbr
    }

    table_data['data'] = table.get_data_rows()
    return table_data
