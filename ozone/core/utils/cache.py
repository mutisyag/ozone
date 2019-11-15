import concurrent.futures
import requests

from django.conf import settings


pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)


class ConfigurationError(Exception):
    pass


def invalidate_aggregation_cache(instance):
    """
    Used to invalidate the aggregation cache based on the instance that was
    added/modified/deleted.

    For now, due to limitations on the Drupal side, invalidation works by
    invalidating all data for a specific party.
    """
    url = settings.CACHE_INVALIDATON_URL
    try:
        timeout = float(settings.CACHE_INVALIDATION_TIMEOUT)
    except ValueError:
        raise ConfigurationError(
            'CACHE_INVALIDATION_TIMEOUT needs to be a numeric value'
        )
    if url is None:
        return

    print('Invalidating')

    # TODO: send this to the pool
    # This will timeout even if it receives data
    requests.get(url, timeout=timeout)

    print('Done invalidating')
