from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder

from ..reporting import Submission


class TransitionEvent(models.Model):
    """
    Generic transition events in a submission's life cycle.
    """
    # We'd rather couple this with the submission rather than the workflow
    # instance, as it makes modelling and referencing clearer.
    submission = models.ForeignKey(
        Submission, related_name='transition_events' ,on_delete=models.PROTECT
    )
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)

    transition = models.CharField(max_length=60)
    from_state = models.CharField(max_length=60)
    to_state = models.CharField(max_length=60)
    extra = JSONField(encoder=DjangoJSONEncoder, null=True)

    class Meta:
        verbose_name = 'workflow event'
        unique_together = ('timestamp', 'object_id', 'from_state', 'to_state')
