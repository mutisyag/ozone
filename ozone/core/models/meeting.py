import enum

from django.db import models

__all__ = [
    'ExemptionTypes',
    'Meeting',
    'Treaty',
    'Decision',
]


@enum.unique
class ExemptionTypes(enum.Enum):
    """
    General enum of ratification types; should be useful in other models too
    """
    CRITICAL = 'Critical use'
    ESSENTIAL = 'Essential use'
    HIGH_AMBIENT = 'High ambient'
    PROCESS_AGENT = 'Process agent'
    LABORATORY = 'Laboratory'
    OTHER = 'Other'


class Meeting(models.Model):
    """
    Information on Ozone-related meetings
    """

    meeting_id = models.CharField(max_length=16, unique=True)

    treaty_flag = models.BooleanField(default=False)

    # Two existing data fields have null start/end dates
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    # No need for anything else than a CharField
    location = models.CharField(max_length=128)

    description = models.CharField(max_length=128)

    def __str__(self):
        return self.description

    class Meta:
        ordering = ('pk',)


class Treaty(models.Model):
    """
    Information on Ozone-related treaties
    """

    treaty_id = models.CharField(max_length=16, unique=True)

    name = models.CharField(max_length=64, unique=True)

    meeting_id = models.ForeignKey(
        Meeting, related_name='treaty', on_delete=models.PROTECT
    )

    date = models.DateField()

    entry_into_force_date = models.DateField()

    base_year = models.IntegerField(null=True)

    description = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'treaties'


class Decision(models.Model):
    """
    Decision
    """

    decision_id = models.CharField(max_length=16, unique=True)

    meeting = models.ForeignKey(
        Meeting, related_name='decisions', on_delete=models.PROTECT
    )

    name = models.CharField(max_length=256, unique=True)

    remark = models.CharField(max_length=256, blank=True)
