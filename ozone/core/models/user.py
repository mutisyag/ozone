from django.contrib.auth.models import AbstractUser
from django.db import models

from guardian.mixins import GuardianUserMixin

from .party import Party


class User(GuardianUserMixin, AbstractUser):

    party = models.ForeignKey(
        Party, related_name='users',
        null=True,
        blank=True,
        on_delete=models.PROTECT
    )

    is_secretariat = models.BooleanField(default=False)

    # Both Party and Secretariat users can be read-only
    is_read_only = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'user'
