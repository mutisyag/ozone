from django.db import models

from .party import Party
from .reporting import ReportingPeriod

__all__ = [
    'ProcessAgentContainTechnology',
]


class ProcessAgentContainTechnology(models.Model):
    """
    Reported containment technologies
    """

    # TODO: shouldn't this have a Submission?
    reporting_period = models.ForeignKey(
        ReportingPeriod, on_delete=models.PROTECT
    )

    party = models.ForeignKey(
        Party, on_delete=models.PROTECT
    )

    contain_technology = models.CharField(max_length=9999)
