from django.core.exceptions import ObjectDoesNotExist

from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import Blend, Submission, Party


class IsSecretariatOrSamePartySubmission(BasePermission):
    """
    This is used for evaluating permissions on Submission views.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        # Definitely not a safe method :)
        sub_pk = view.kwargs.get('pk', None)
        if sub_pk:
            # Submission object already exists.
            submission = Submission.objects.get(pk=sub_pk)
            return submission.has_edit_rights(request.user)
        else:
            # It's a create
            party = Party.objects.get(id=request.data.get('party', None))
            return Submission.has_create_rights_for_party(party, request.user)

    def has_object_permission(self, request, view, obj):
        if request.method not in SAFE_METHODS:
            return obj.has_edit_rights(request.user)
        return obj.has_read_rights(request.user)


class IsSecretariatOrSamePartySubmissionRemarks(BasePermission):
    """
    This is used for evaluating permissions on Submission-related views (e.g.
    Article 7 reports etc).
    `submission_pk` will *always* be set to something in this case.
    """
    def has_permission(self, request, view):
        submission = Submission.objects.get(
            pk=view.kwargs.get('submission_pk', None)
        )
        if request.method not in SAFE_METHODS:
            # The serializer will look more closely at the modified fields
            return submission.can_edit_remarks(request.user)
        else:
            # Whoever can view the submission can also view its remarks
            return submission.has_read_rights(request.user)

    def has_object_permission(self, request, view, obj):
        if request.method not in SAFE_METHODS:
            return obj.can_edit_remarks(request.user)
        return obj.has_read_rights(request.user)


class IsSecretariatOrSamePartySubmissionFlags(BasePermission):
    """
    This is used for evaluating permissions on Submission-related views (e.g.
    Article 7 reports etc).
    `submission_pk` will *always* be set to something in this case.
    """
    def has_permission(self, request, view):
        if request.method not in SAFE_METHODS:
            submission = Submission.objects.get(
                pk=view.kwargs.get('submission_pk', None)
            )
            # The serializer will look more closely at the modified fields
            return len(submission.get_changeable_flags(request.user)) > 0

        # No need to call has_read_rights here, as queryset is filtered
        return True

    def has_object_permission(self, request, view, obj):
        if request.method not in SAFE_METHODS:
            return len(obj.get_changeable_flags(request.user)) > 0
        return obj.submission.has_read_rights(request.user)


class IsSecretariatOrSamePartySubmissionRelated(BasePermission):
    """
    This is used for evaluating permissions on Submission-related views (e.g.
    Article 7 reports etc) for models that have a submission as FK.
    `submission_pk` will *always* be set to something in this case.
    """
    def has_permission(self, request, view):
        if request.method not in SAFE_METHODS:
            submission = Submission.objects.get(
                pk=view.kwargs.get('submission_pk', None)
            )
            return submission.has_edit_rights(request.user)
        # No need to call has_read_rights here, as queryset is filtered
        return True

    def has_object_permission(self, request, view, obj):
        if request.method not in SAFE_METHODS:
            return obj.submission.has_edit_rights(request.user)
        return obj.submission.has_read_rights(request.user)


class IsSecretariatOrSamePartyBlend(BasePermission):
    """
    This is used for evaluating permissions on Blend views.
    """
    def has_permission(self, request, view):
        if request.method not in SAFE_METHODS:
            blend_pk = view.kwargs.get('pk', None)
            if blend_pk:
                # Blend object already exists.
                blend = Blend.objects.get(pk=blend_pk)
                return blend.has_edit_rights(request.user)
            else:
                # It's a create
                party = Party.objects.get(id=request.data.get('party', None))
                return Blend.has_create_rights_for_party(party, request.user)

        return True

    def has_object_permission(self, request, view, obj):
        if request.method not in SAFE_METHODS:
            return obj.has_edit_rights(request.user)
        return obj.has_read_rights(request.user)
