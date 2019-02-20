from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

__all__ = [
    'ReportingPeriod'
]


class ReportingPeriod(models.Model):
    """
    Period for which data is submitted.

    There is definitely a need to support non-standard reporting periods.
    """

    # TODO: how will these be used in the event of one-time reports?
    # The system could create a custom period based on the date(s) the transfer
    # took place, but that seems a bit overkill.

    # This will usually be '2017', '2018' etc; most periods (but not all!)
    # are mapped to calendar years
    name = models.CharField(max_length=64, unique=True)

    is_reporting_allowed = models.BooleanField(
        default=True,
        help_text="Indicates whether reporting can be performed for this "
        "reporting period. Will be False for baseline years."
    )

    is_reporting_open = models.BooleanField(
        default=False,
        help_text="Indicates whether reporting is open/ongoing for this "
        "reporting period."
    )

    # this is always required, and can be in the future
    start_date = models.DateField()

    # we are always working with 'closed interval' reporting periods
    # TODO: is above assumption really true? what about one-time reports?
    end_date = models.DateField()

    description = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_current_period(cls):
        today = datetime.now().date()
        return cls.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
        ).first()

    @classmethod
    def get_most_recent(cls):
        return (
            cls.objects.filter(is_reporting_open=True)
            .order_by('-start_date')
            .first()
        )

    def clean(self):
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError(
                {
                    'end_date': [_(
                        "End date has to be temporally after start date."
                    )]
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        db_table = 'reporting_period'
