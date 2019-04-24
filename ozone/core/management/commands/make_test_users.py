"""Create/remove a set of test users, or individual ones. With parties chosen at random unless
otherwise specified. (Romania and EU are excluded). Default users created:
party, party_ro, secretariat, secretariat_ro, eu, eu_ro.
"""
import copy
import random
import logging

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.db.models import F
from django.db.models import Q

from ozone.core.models.user import User
from ozone.core.models.party import Party


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = __doc__

    default_users = {
        "admin": {
            "party": None,
            "is_secretariat": True,
            "is_read_only": False,
            "is_superuser": True,
            "is_staff": True,
        },
        "secretariat": {
            "party": None,
            "is_secretariat": True,
            "is_read_only": False,
            "is_staff": True,
        },
        "secretariat_ro": {
            "party": None,
            "is_secretariat": True,
            "is_read_only": True,
            "is_staff": True,
        }
    }

    def add_arguments(self, parser):
        parser.add_argument('user', nargs="?",
                            help="Only add this user instead of the default list")
        parser.add_argument('--remove', action="store_true", default=False,
                            help="Remove the users instead of adding them")
        parser.add_argument('-P', '--party', default=None,
                            help="Choose what party to assign the users to, instead "
                                 "of choosing at random. (Abbreviation)")
        parser.add_argument('-S', '--is-secretariat', action="store_true", default=False,
                            help="Create the user as a secretariat, when adding a single user")
        parser.add_argument('-RO', '--is-read-only', action="store_true", default=False,
                            help="Create the user as read-only, when adding a single user")

    def handle(self, *args, **options):
        stream = logging.StreamHandler()
        stream.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s'
        ))
        logger.addHandler(stream)
        logger.setLevel(logging.INFO)

        if int(options['verbosity']) > 1:
            logger.setLevel(logging.DEBUG)

        all_parties = Party.objects.exclude(
            ~Q(parent_party_id=F('id'))
        )

        if not options["user"]:
            to_create = copy.deepcopy(self.default_users)
            for party in all_parties:
                user = 'party_' + party.abbr.lower()
                to_create[user] = {}
                to_create[user]['party'] = party
                to_create[user]['is_read_only'] = False
                # And read-only user
                user_ro = 'party_' + party.abbr.lower() + '_ro'
                to_create[user_ro] = {}
                to_create[user_ro]['party'] = party
                to_create[user_ro]['is_read_only'] = True
        else:
            party = random.choice(all_parties)
            if options['party']:
                party = Party.objects.get(abbr=options['party'].upper())
            to_create = {
                options["user"]: {
                    "party": party,
                    "is_secretariat": options["is_secretariat"],
                    "is_read_only": options["is_read_only"],
                }
            }

        if options['remove']:
            User.objects.filter(username__in=list(to_create.keys())).delete()
            logger.info("Users removed")
        else:
            for user, details in to_create.items():
                try:
                    obj = User.objects.create_user(
                        user,
                        email="%s@example.com" % user,
                        password=user,
                        **details,
                    )
                    obj.save()
                    logger.info("Created user %s %s", user, details)
                except IntegrityError:
                    logger.warning("%s already existed, skipping.", user)
                    continue

            # Create Secretariat group and assign secretariat and secretariat_ro
            # to this group.
            if not Group.objects.filter(name='Secretariat'):
                group = Group.objects.create(name='Secretariat')
                group.permissions.set(
                    Permission.objects.filter(
                        content_type__app_label='core'
                    ).exclude(name__startswith='Can chart')
                )
                group.user_set.add(User.objects.get(username='secretariat'))
                group.user_set.add(User.objects.get(username='secretariat_ro'))
                logger.info(
                    "Created group Secretariat and "
                    "added secretariat and secretariat_ro users"
                )
            else:
                logger.warning("Group Secretariat already exists, skipping.")
