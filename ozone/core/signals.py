from django.dispatch import receiver

from .utils.cache import invalidate_aggregation_cache

import django.dispatch


clear_cache = django.dispatch.Signal()


@receiver(clear_cache)
def clear_aggregation_cache(sender, instance, **kwargs):
    """
    Handler for the clear_cache signal
    """
    print(f'invalidating the cache for {instance}')
    invalidate_aggregation_cache(instance)
