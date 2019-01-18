from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import Blend, Submission


def is_secretariat_or_admin(request):
    return request.user.is_secretariat or request.user.is_superuser


class BaseIsSecretariatOrSameParty(BasePermission):

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
        """
        pass

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
        """
        pass


class IsSecretariatOrSamePartySubmission(BaseIsSecretariatOrSameParty):

    @staticmethod
    def has_same_party(request, view):
        if request.method not in SAFE_METHODS and not is_secretariat_or_admin(request):
            sub_pk = view.kwargs.get('pk', None)
            if sub_pk:
                # Submission object already exists.
                party = Submission.objects.get(pk=sub_pk).party.pk
            else:
                # It's a create
                party = request.data.get('party', None)
            return party == request.user.party.pk
        return True

    def has_object_permission(self, request, view, obj):
        if is_secretariat_or_admin(request):
            return True
        return request.user.party == obj.party


class IsSecretariatOrSamePartySubmissionRelated(BaseIsSecretariatOrSameParty):

    @staticmethod
    def has_same_party(request, view):
        if request.method not in SAFE_METHODS and not is_secretariat_or_admin(request):
            party = Submission.objects.get(
                pk=view.kwargs.get('submission_pk', None)
            ).party
            return party == request.user.party
        return True

    def has_object_permission(self, request, view, obj):
        if is_secretariat_or_admin(request):
            return True
        return request.user.party == obj.submission.party


class IsSecretariatOrSamePartyBlend(BaseIsSecretariatOrSameParty):

    @staticmethod
    def has_same_party(request, view):
        if request.method not in SAFE_METHODS and not is_secretariat_or_admin(request):
            blend_pk = view.kwargs.get('pk', None)
            if blend_pk:
                # Blend object already exists.
                party = Blend.objects.get(pk=blend_pk).party.pk
            else:
                # It's a create
                party = request.data.get('party', None)
            return party == request.user.party.pk
        return True

    def has_object_permission(self, request, view, obj):
        if is_secretariat_or_admin(request):
            return True
        return request.user.party == obj.party
