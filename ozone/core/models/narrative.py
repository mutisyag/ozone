from django.db import models

from .reporting import Submission

__all__ = [
    'ProcessAgentContainTechnology',
]


class ProcessAgentContainTechnology(models.Model):
    """
    Reported containment technologies
    """

    submission = models.ForeignKey(
        Submission,
        related_name='pa_contain_technologies',
        on_delete=models.PROTECT
    )

    contain_technology = models.CharField(max_length=9999)

    class Meta:
        db_table = 'pa_contain_technology'
