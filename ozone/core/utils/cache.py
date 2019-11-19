import concurrent.futures
import logging
import requests
from requests.auth import HTTPBasicAuth

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
    if url is None:
        return
    try:
        timeout = float(settings.CACHE_INVALIDATION_TIMEOUT)
    except ValueError:
        logger.error(
            'Error while invalidating cache. '
            'CACHE_INVALIDATION_TIMEOUT needs to be a numeric value.'
        )
        timeout = 0

    logger.info(f'Invalidating cache for party {party_id}')

    # requests.get() will timeout after `timeout` even if it receives data
    auth = HTTPBasicAuth(
        settings.CACHE_INVALIDATION_USER, settings.CACHE_INVALIDATION_PASS
    )
    url = f'{url}?party={party_id}'
    pool.submit(requests.get, url, timeout=timeout, auth=auth)

    logger.info('Done invalidating')


def invalidate_aggregation_cache(instance):
    """
    Used to invalidate entries in the aggregation cache based on the ProdCons
    instance that was added/modified/deleted.
    """
    invalidate_party_cache(instance.party.id)


def invalidate_aggregations_cache(aggregation_dict_list):
    """
    Used to invalidate entries in the aggregation cache based on a list of
    group/party/period dicts corresponding to a number of ProdCons instances
    that were modified.
    """
    party_id_set = set([item['party'] for item in aggregation_dict_list])
    for party_id in party_id_set:
        invalidate_party_cache(party_id)


def invalidate_focal_point_cache(instance):
    """
    Used to invalidate entries in the focal point cache based on the FocalPoint
    instance that was added/modified/deleted.
    """
    invalidate_party_cache(instance.party.id)


def invalidate_ratification_cache(instance):
    """
    Used to invalidate entries in the ratification cache based on the
    Ratification instance that was added/modified/deleted.
    """
    invalidate_party_cache(instance.party.id)
