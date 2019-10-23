from django.core.signals import request_finished
from django.dispatch import receiver

from .utils.cache import invalidate_aggregation_cache

import django.dispatch


clear_cache = django.dispatch.Signal(providing_args=['clear_cache',])


@receiver(clear_cache)
def clear_aggregation_cache(sender, instance, **kwargs):
    """
    Handler for the clear_cache signal
    """
    print('invalidating the cache')
    invalidate_aggregation_cache(instance)


# TODO: remove when done
@receiver(request_finished)
def printdfdf(sender, **kwargs):
    print('\n***Request processing finished***\n')
