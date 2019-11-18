import concurrent.futures
import logging
import requests

from django.conf import settings


pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)


logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


def invalidate_aggregation_cache(instance):
    """
    Used to invalidate the aggregation cache based on the instance that was
    added/modified/deleted.

    For now, due to limitations on the Drupal side, invalidation works by
    invalidating all data for a specific party.
    """
    url = settings.CACHE_INVALIDATION_URL
    try:
        timeout = float(settings.CACHE_INVALIDATION_TIMEOUT)
    except ValueError:
        logger.error(
            'Error while invalidating cache. '
            'CACHE_INVALIDATION_TIMEOUT needs to be a numeric value.'
        )
    if url is None:
        return

    logger.info('Invalidating')

    # requests.get() will timeout after `timeout` even if it receives data
    url = f'{url}?party={instance.party}'
    pool.submit(requests.get, url, timeout=timeout)

    logger.info('Done invalidating')
