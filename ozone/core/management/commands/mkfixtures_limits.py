import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.serializers.json import DjangoJSONEncoder

from ozone.core.models import (
    Baseline,
    ControlMeasure,
    Group,
    LimitTypes,
    Party,
    PartyHistory
)


class Command(BaseCommand):
    help = "Calculate Limits and generate fixtures."

    OUTPUT_DIR = settings.FIXTURE_DIRS[0]

    def handle(self, *args, **options):
        if not ControlMeasure.objects.exists():
            print(
                "Control measures not found. Please, "
                "import control measure fixtures."
            )
            return
        data = []
        idx = 1
        for party_history in PartyHistory.objects.all():
            party = party_history.party
            party_type = party_history.party_type
            period = party_history.reporting_period
            for group in Group.objects.all():
                cm_queryset = ControlMeasure.objects.filter(
                    group=group,
                    party_type=party_type,
                    end_date__gte=period.start_date,
                    start_date__lte=period.end_date
                ).order_by('start_date')
                for limit_type in LimitTypes:
                    cm_queryset_by_limit_type = cm_queryset.filter(
                        limit_type=limit_type.value
                    )
                    length = cm_queryset_by_limit_type.count()
                    if length == 0:
                        continue
                    elif length == 1:
                        cm = cm_queryset_by_limit_type.first()
                        baseline = Baseline.objects.filter(
                            party=party,
                            group=group,
                            baseline_type=cm.baseline_type
                        ).first()
                        if not baseline or baseline.baseline is None:
                            continue
                        limit = baseline.baseline * cm.allowed
                        data.append(
                            self.get_entry(idx, party, period, group, limit_type.value, limit)
                        )
                        idx += 1
                    elif length == 2:
                        cm1 = cm_queryset_by_limit_type[0]
                        cm2 = cm_queryset_by_limit_type[1]
                        baseline1 = Baseline.objects.filter(
                            party=party,
                            group=group,
                            baseline_type=cm1.baseline_type
                        ).first()
                        baseline2 = Baseline.objects.filter(
                            party=party,
                            group=group,
                            baseline_type=cm2.baseline_type
                        ).first()
                        if (
                            not baseline1
                            or baseline1.baseline is None
                            or not baseline2
                            or baseline2.baseline is None
                        ):
                            continue
                        days1 = (cm1.end_date - period.start_date).days + 1
                        days2 = (period.end_date - cm2.start_date).days + 1
                        limit = round(
                            (
                                baseline1.baseline * cm1.allowed * days1
                                + baseline2.baseline * cm2.allowed * days2
                            ) / ((period.end_date - period.start_date).days + 1),
                            2
                        )
                        data.append(
                            self.get_entry(idx, party, period, group, limit_type.value, limit)
                        )
                        idx += 1

        filename = os.path.join(self.OUTPUT_DIR, 'limits.json')
        with open(filename, 'w', encoding="utf-8") as outfile:
            json.dump(
                data, outfile,
                indent=2, ensure_ascii=False, sort_keys=True,
                cls=DjangoJSONEncoder
            )
        print('Done with %s' % filename)

    def get_entry(self, idx, party, period, group, limit_type, limit):
        return {
            'pk': idx,
            'model': 'core.limit',
            'fields': {
                'party': party.pk,
                'reporting_period': period.pk,
                'group': group.pk,
                'limit_type': limit_type,
                'limit': limit
            }
        }
