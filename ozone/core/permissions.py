from django.core.exceptions import ObjectDoesNotExist

from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import Party, Submission


def is_secretariat_or_admin(request):
    return request.user.is_secretariat or request.user.is_superuser


class IsSecretariatOrSameParty(BasePermission):

    @staticmethod
    def has_same_party(request, view):
        """
        Allows us to verify that the user making the request is not trying to
        create an object for a Party he does not belong to.

        Needed on:
        - create: because `get_object_permission` only works for
          already-existing objects, so does not apply to object creation.
        - update: to verify that party is not changed to something the user
          cannot create objects for

        This is only to be used for Submission and data reporting models!
        """
        if request.method not in SAFE_METHODS and \
                not is_secretariat_or_admin(request):
            # Get the party either directly (for Submission objects),
            # or from the referenced submission
            if hasattr(view, 'queryset') and view.queryset:
                queryset = view.queryset
            else:
                queryset = view.get_queryset()

            try:
                if queryset.model == Submission:
                    party = Party.objects.get(
                        pk=request.data.get('party', None)
                    )
                else:
                    party = Submission.objects.get(
                        pk=view.kwargs.get('submission_pk', None)
                    ).party
                if party != request.user.party:
                    return False
            except ObjectDoesNotExist:
                # Could not find a party matching the request data, so simply
                # return a sage default
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
        if is_secretariat_or_admin(request):
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
        if is_secretariat_or_admin(request):
            return True

        if isinstance(obj, Submission):
            object_party = obj.party
        else:
            object_party = obj.submission.party
        return request.user.party == object_party
