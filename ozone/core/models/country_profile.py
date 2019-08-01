from django.db import models

from . import Party, Submission


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
        null=True
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
        null=True
    )

    ordering_id = models.IntegerField(default=0)

    class Meta:
        db_table = "focal_point"
