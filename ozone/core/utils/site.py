from django.contrib.sites.models import Site


def get_site_name():
    """ Return the name of the first site we find, or the empty string """
    site = Site.objects.all().first()
    return site.name if site else ""
