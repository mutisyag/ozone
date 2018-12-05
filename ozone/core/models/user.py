from django.contrib.auth.models import AbstractUser
from django.db import models

from guardian.mixins import GuardianUserMixin
from rest_framework.authtoken.models import Token

from .party import Party


class User(GuardianUserMixin, AbstractUser):

    party = models.ForeignKey(
        Party, related_name='users',
        null=True,
        blank=True,
        on_delete=models.PROTECT
    )

    is_secretariat = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Create authentication token only on first-time save
        first_save = False
        if not self.pk or kwargs.get('force_insert', False):
            first_save = True

        super().save(*args, **kwargs)
        if first_save:
            Token.objects.create(user=self)

    class Meta:
        verbose_name = 'user'
