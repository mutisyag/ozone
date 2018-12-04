from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import Party, Submission


class IsSecretariatOrSameParty(BasePermission):
    @staticmethod
    def has_same_party(request, view):
        """
        Allows us to verify that the user making the request is not trying to
        create an object for a Party he does not belong to.

        Needed because `get_object_permission` only works for already-existing
        objects, so does not apply to object creation.

        This is only to be used for Submission and data reporting models!
        """
        if request.method == 'POST' and request.user.is_secretariat is False:
            # Get the party either directly (for Submission objects),
            # or from the referenced submission
            if view.queryset.model == Submission:
                party = Party.objects.get(pk=request.data.get('party', None))
            else:
                party = Submission.objects.get(
                    pk=request.data.get('submission', None)
                    ).party
            if party != request.user.party:
                return False

        return True

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

        # It's a Party write user and a write request - calling has_same_party
        # to make sure user is not trying to create an obj for different party
        return self.has_same_party(request, view)

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
