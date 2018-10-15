from django.contrib.auth.models import AbstractUser

from guardian.mixins import GuardianUserMixin


class User(GuardianUserMixin, AbstractUser):

    class Meta:
        verbose_name = 'user'
