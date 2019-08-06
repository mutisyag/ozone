from django.db import models

from . import Obligation, Party, ReportingPeriod, Submission


def user_directory_path(instance, filename):
    return filename


class OtherCountryProfileData(models.Model):

    party = models.ForeignKey(
        Party,
        related_name='other_country_profile_data',
        on_delete=models.PROTECT
    )
    reporting_period = models.ForeignKey(
        ReportingPeriod,
        related_name='other_country_profile_data',
        on_delete=models.PROTECT
    )
    obligation = models.ForeignKey(
        Obligation,
        related_name='other_country_profile_data',
        on_delete=models.PROTECT
    )
    submission = models.ForeignKey(
        Submission,
        related_name='other_country_profile_data',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    description = models.CharField(max_length=9999, blank=True)

    file = models.FileField(
        upload_to=user_directory_path, blank=True, null=True
    )
    url = models.URLField(
        'URL', max_length=1024, null=True, blank=True
    )
    remarks_secretariat = models.CharField(max_length=9999, blank=True)

    class Meta:
        db_table = "other_country_profile_data"
        verbose_name_plural = "other country profile data"


class Website(models.Model):
    party = models.ForeignKey(
        Party, related_name='websites', on_delete=models.PROTECT
    )

    file = models.FileField(
        upload_to=user_directory_path, blank=True, null=True
    )

    url = models.URLField(
        'URL', max_length=1024, null=True, blank=True
    )
    description = models.CharField(max_length=9999, blank=True)
    is_url_broken = models.BooleanField(default=False)

    ordering_id = models.IntegerField(default=0)

    class Meta:
        db_table = "website"


class LicensingSystem(models.Model):
    party = models.ForeignKey(
        Party, related_name='licensing_systems', on_delete=models.PROTECT
    )
    has_ods = models.BooleanField(default=False)
    date_reported_ods = models.DateField(null=True)
    has_hfc = models.BooleanField(default=False)
    date_reported_hfc = models.DateField(null=True)
    remarks = models.CharField(max_length=9999, blank=True)

    submission = models.ForeignKey(
        Submission,
        related_name='licensing_systems',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    class Meta:
        db_table = "licensing_system"


class FocalPoint(models.Model):
    party = models.ForeignKey(
        Party, related_name='focal_points', on_delete=models.PROTECT
    )
    name = models.CharField(max_length=256, blank=True)
    designation = models.CharField(max_length=512, blank=True)
    tel = models.CharField(max_length=128, blank=True)
    email = models.CharField(max_length=256, blank=True)
    fax = models.CharField(max_length=256, blank=True)
    address = models.CharField(max_length=9999, blank=True)

    is_licensing_system = models.BooleanField(default=False)
    is_national = models.BooleanField(default=False)

    submission = models.ForeignKey(
        Submission,
        related_name='focal_points',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    ordering_id = models.IntegerField(default=0)

    class Meta:
        db_table = "focal_point"
