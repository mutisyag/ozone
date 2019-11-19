import concurrent.futures
import logging
import requests

from django.conf import settings


pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)


logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


def invalidate_party_cache(party_id):
    """
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

    logger.info(f'Invalidating cache for party {party_id}')

    # requests.get() will timeout after `timeout` even if it receives data
    url = f'{url}?party={party_id}'
    pool.submit(requests.get, url, timeout=timeout)

    logger.info('Done invalidating')


def invalidate_aggregation_cache(instance):
    """
    Used to invalidate the aggregation cache based on the ProdCons instance that
    was added/modified/deleted.
    """
    invalidate_party_cache(instance.party.id)


def invalidate_focal_point_cache(instance):
    """
    Used to invalidate the focal point cache based on the FocalPoint instance
    that was added/modified/deleted.
    """
    invalidate_party_cache(instance.party.id)
