from django.dispatch import receiver

from .utils.cache import invalidate_aggregation_cache
from .utils.cache import invalidate_focal_point_cache
from .utils.cache import invalidate_ratification_cache

import django.dispatch


# Signals to be received
clear_aggregation_cache_signal = django.dispatch.Signal()
clear_focal_point_cache_signal = django.dispatch.Signal()
clear_ratification_cache_signal = django.dispatch.Signal()


@receiver(clear_aggregation_cache_signal)
def clear_aggregation_cache(sender, instance, **kwargs):
    """
    Handler for the clear_cache signal
    """
    invalidate_aggregation_cache(instance)


@receiver(clear_focal_point_cache_signal)
def clear_focal_point_cache(sender, instance, **kwargs):
    """
    Handler for the clear_cache signal
    """
    invalidate_focal_point_cache(instance)


@receiver(clear_ratification_cache_signal)
def clear_ratification_cache(sender, instance, **kwargs):
    """
    Handler for the clear_cache signal
    """
    invalidate_ratification_cache(instance)
