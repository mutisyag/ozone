from django.db import models

__all__ = [
    'Meeting',
    'Treaty',
    'Decision',
]


class Meeting (models.Model):
    """
    Information on Ozone-related meetings
    """

    meeting_id = models.CharField(max_length=16, unique=True)

    treaty_flag = models.BooleanField(default=False)

    # Two existing data fields have null start/end dates
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)

    # No need for anything else than a CharField
    location = models.CharField(max_length=128)

    description = models.CharField(max_length=128)


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


class Decision(models.Model):
    """
    Decision
    """

    decision_id = models.CharField(max_length=16, unique=True)

    meeting = models.ForeignKey(
        Meeting, related_name='decisions', on_delete=models.PROTECT
    )

    name = models.CharField(max_length=256, unique=True)

    remarks = models.CharField(max_length=256, blank=True)
