from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, F

from guardian.mixins import GuardianUserMixin
from rest_framework.authtoken.models import Token

from .party import Party, Language


class User(GuardianUserMixin, AbstractUser):

    party = models.ForeignKey(
        Party, related_name='users',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        limit_choices_to=Q(parent_party_id=F('id'))
    )
    created_by = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    activated = models.BooleanField(default=True)

    is_secretariat = models.BooleanField(default=False)

    # Both Party and Secretariat users can be read-only
    is_read_only = models.BooleanField(default=True)

    language = models.ForeignKey(
        Language,
        related_name='users',
        null=True,
        blank=True,
        on_delete=models.PROTECT
    )

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
