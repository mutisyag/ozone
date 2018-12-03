from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import Submission


class IsSecretariatOrSameParty(BasePermission):
    def has_permission(self, request, view):
        """
        Called for all HTTP methods. Assumes user is already authenticated.
        """
        # Allow any read requests (the view's queryset takes care of filtering
        # out inaccessible objects)
        if request.method in SAFE_METHODS:
            return True

        # Request is write, filter out read-only users
        if request.user.is_read_only:
                return False

        # At this point request is write, user is write
        if request.user.is_secretariat:
            return True

        # It's a Party write user and a write request - we return True and
        # let has_object_permission or the view's create() handle this
        return True

    def has_object_permission(self, request, view, obj):
        """
        Called for HTTP methods that require an object.
        This is only called if has_permission() has already passed.

        Only applicable to submissions or objects related to a submission
        (i.e. data reports)
        """
        if isinstance(obj, Submission):
            object_party = obj.party
        else:
            object_party = obj.submission.party

        return request.user.is_secretariat or request.user.party == object_party
