"""Create/remove a set of test users, or individual ones. With parties chosen at random unless
otherwise specified. (Romania and EU are excluded). Default users created:
party, party_ro, secretariat, secretariat_ro, eu, eu_ro.
"""
import copy
import random
import logging

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from ozone.core.models.user import User
from ozone.core.models.party import Party


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = __doc__

    default_users = {
        "party": {
            "party": None,
            "is_secretariat": False,
            "is_read_only": False,
        },
        "party_ro": {
            "party": None,
            "is_secretariat": False,
            "is_read_only": True,
        },
        "secretariat": {
            "party": None,
            "is_secretariat": True,
            "is_read_only": False,
        },
        "secretariat_ro": {
            "party": None,
            "is_secretariat": True,
            "is_read_only": True,
        },
        "eu": {
            "party": "ECE",
            "is_secretariat": False,
            "is_read_only": False,
        },
        "eu_ro": {
            "party": "ECE",
            "is_secretariat": False,
            "is_read_only": True,
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

        if options["user"]:
            to_create = {
                options["user"]: {
                    "party": None,
                    "is_secretariat": options["is_secretariat"],
                    "is_read_only": options["is_read_only"],
                }
            }
        else:
            to_create = copy.deepcopy(self.default_users)

        all_parties = Party.objects.exclude(
            abbr__in=["RO", "ECE"]
        ).all()

        for user in to_create.values():
            if user['party'] is not None:
                user['party'] = Party.objects.get(abbr=user['party'].upper())
            elif user["party"] is None and options['party']:
                user['party'] = Party.objects.get(abbr=options['party'].upper())
            else:
                user['party'] = random.choice(all_parties)

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
