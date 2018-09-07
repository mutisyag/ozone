from django.db import models

from .meeting import Decision
from .reporting import Submission
from .substance import Substance, Blend


__all__ = [
    'Article7Questionnaire',
    'Article7Exports',
]


class BaseReport(models.Model):
    """
    This will be used as a base for all reporting models.
    """

    # Django syntax for generating proper related_name in concrete model
    submission = models.ForeignKey(
        Submission, related_name='%(class)ss', on_delete=models.PROTECT
    )

    remarks_party = models.CharField(max_length=512, blank=True)
    remarks_os = models.CharField(max_length=512, blank=True)

    class Meta:
        abstract = True


class Article7Questionnaire(BaseReport):
    """
    Model for a simple Article 7 Questionnaire report row
    """

    has_imports = models.BooleanField()

    has_exports = models.BooleanField()

    has_produced = models.BooleanField()

    has_destroyed = models.BooleanField()

    has_nonparty = models.BooleanField()

    has_emissions = models.BooleanField()

    class Meta:
        db_table = 'reporting_article_seven_questionnaire'


class Article7Exports(BaseReport):
    """
    Model for a simple Article 7 Questionnaire report
    """

    # TODO: ensure that one and only one of these two is non-null
    substance = models.ForeignKey(
        Substance, null=True, on_delete=models.PROTECT
    )
    blend = models.ForeignKey(
        Blend, null=True, on_delete=models.PROTECT
    )

    quantity_total_new = models.PositiveIntegerField(null=True)

    quantity_total_recovered = models.PositiveIntegerField(null=True)

    quantity_feedstock = models.PositiveIntegerField(null=True)

    decision = models.ForeignKey(
        Decision, null=True, on_delete=models.PROTECT
    )

    class Meta:
        db_table = 'reporting_article_seven_exports'
