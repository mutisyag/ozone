import json
import os

from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q

from ozone.core.models import (
    Baseline,
    ControlMeasure,
    Group,
    LimitTypes,
    Party,
    PartyHistory,
    ProdCons,
)
from ozone.core.models.utils import round_decimal_half_up


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
            if period.name in ["C1999", "C2000", "C2001"]:
                # No limits for control periods
                continue
            print('Processing country {} and period {}'.format(party.name, period.name))
            if period.name == 'BaseA5' or period.name == 'BaseNA5':
                continue
            for group in Group.objects.all():
                cm_queryset = ControlMeasure.objects.filter(
                    group=group,
                    party_type=party_type,
                    start_date__lte=period.end_date
                ).filter(
                    Q(end_date__gte=period.start_date) | Q(end_date__isnull=True)
                ).order_by('start_date')
                for limit_type in LimitTypes:
                    if limit_type.value in [
                        LimitTypes.BDN.value,
                        LimitTypes.PRODUCTION.value
                    ] and party.abbr == 'EU':
                        # No BDN or Prod limits for EU/ECE(European Union)
                        continue
                    if limit_type.value in [
                        LimitTypes.CONSUMPTION.value
                    ] and party in Party.get_eu_members_at(period.name):
                        # No consumption baseline for EU member states
                        continue
                    cm_queryset_by_limit_type = cm_queryset.filter(
                        limit_type=limit_type.value
                    )
                    length = cm_queryset_by_limit_type.count()
                    if length == 0:
                        continue
                    elif length == 1:
                        cm = cm_queryset_by_limit_type.first()
                        if group.group_id == 'CII' or group.group_id == 'CIII':
                            baseline = 0
                        else:
                            baseline = Baseline.objects.filter(
                                party=party,
                                group=group,
                                baseline_type=cm.baseline_type
                            ).first()
                            if not baseline or baseline.baseline is None:
                                continue
                            else:
                                baseline = baseline.baseline
                        # TODO: rounding
                        limit = cm.allowed * baseline
                        data.append(
                            self.get_entry(idx, party, period, group, limit_type.value, limit)
                        )
                        idx += 1
                    elif length == 2:
                        # This happens for BDN limits, A/I and E/I, Non-A5 parties
                        if group.group_id == 'CII' or group.group_id == 'CIII':
                            baseline1 = Decimal('0')
                            baseline2 = Decimal('0')
                        else:
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
                                not baseline1 or baseline1.baseline is None
                                or not baseline2 or baseline2.baseline is None
                            ):
                                continue
                            else:
                                baseline1 = baseline1.baseline
                                baseline2 = baseline2.baseline
                        days1 = (cm1.end_date - period.start_date).days + 1
                        days2 = (period.end_date - cm2.start_date).days + 1
                        limit = (
                            (100 * cm1.allowed * days1 * baseline1) / 100
                            + (100 * cm2.allowed * days2 * baseline2) / 100
                        ) / ((period.end_date - period.start_date).days + 1)
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
                'limit': round_decimal_half_up(
                    limit,
                    1 if limit_type == LimitTypes.BDN.value
                    else ProdCons.get_decimals(period, group, party)
                )
            }
        }
