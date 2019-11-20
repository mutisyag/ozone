import django.dispatch
import logging

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from .utils.cache import invalidate_aggregation_cache
from .utils.cache import invalidate_party_cache

from ozone.core.models.party import (
    PartyDeclaration,
    PartyHistory,
    PartyRatification
)
from ozone.core.models.country_profile import (
    FocalPoint,
    IllegalTrade,
    LicensingSystem,
    MultilateralFund,
    ORMReport,
    OtherCountryProfileData,
    ReclamationFacility,
    Website,
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# Signals to be received
clear_aggregation_cache_signal = django.dispatch.Signal()
clear_country_profile_cache_signal = django.dispatch.Signal()


@receiver(clear_aggregation_cache_signal)
def clear_aggregation_cache(sender, instance, **kwargs):
    """
    Handler for the clear_cache signal
    """
    invalidate_aggregation_cache(instance)


def clear_country_profile_cache(sender, instance, **kwargs):
    """
    Clear the cache of the main website
    """
    try:
        invalidate_party_cache(instance.party_id)
    except Exception as e:
        logger.error(
            'Error while invalidating country profile cache. ', e
        )


country_profile_models = [
    FocalPoint,
    IllegalTrade,
    LicensingSystem,
    MultilateralFund,
    ORMReport,
    OtherCountryProfileData,
    PartyDeclaration,
    PartyHistory,
    PartyRatification,
    ReclamationFacility,
    Website,
]
for model in country_profile_models:
    post_save.connect(clear_country_profile_cache, model)
    post_delete.connect(clear_country_profile_cache, model)
