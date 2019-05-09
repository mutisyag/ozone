from datetime import datetime
from base64 import b64encode
from collections import OrderedDict
from copy import deepcopy
from pathlib import Path
import logging
import urllib.parse
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.db.models.query import QuerySet, F
from django.http import HttpResponse
from django_filters import rest_framework as filters
from django.utils.translation import gettext_lazy as _
from impersonate.views import stop_impersonate

from rest_framework import viewsets, mixins, status, generics, views
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import action
from rest_framework.filters import (
    BaseFilterBackend, OrderingFilter, SearchFilter
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.reverse import reverse
from rest_framework.viewsets import GenericViewSet

from ..exceptions import InvalidRequest

from ..models import (
    Region,
    Subregion,
    Party,
    ReportingPeriod,
    ReportingChannel,
    Obligation,
    Submission,
    SubmissionInfo,
    SubmissionFile,
    UploadToken,
    Article7Questionnaire,
    Article7Destruction,
    Article7Production,
    Article7Export,
    Article7Import,
    Article7NonPartyTrade,
    Article7Emission,
    HighAmbientTemperatureProduction,
    HighAmbientTemperatureImport,
    DataOther,
    Group,
    Substance,
    Blend,
    Nomination,
    ExemptionApproved,
    RAFReport,
    SubmissionFormat,
    ProdCons,
    Limit,
)
from ..permissions import (
    IsSecretariatOrSamePartySubmission,
    IsSecretariatOrSamePartySubmissionRemarks,
    IsSecretariatOrSamePartySubmissionFlags,
    IsSecretariatOrSamePartySubmissionClone,
    IsSecretariatOrSamePartySubmissionTransition,
    IsSecretariatOrSamePartySubmissionRelated,
    IsSecretariatOrSamePartyBlend,
    IsCorrectObligation,
    IsSecretariatOrSamePartyUser,
    IsSecretariatOrSafeMethod,
    IsSecretariatOrSamePartyAggregation,
    IsSecretariatOrSamePartyLimit,
)
from ..serializers import (
    CurrentUserSerializer,
    AuthTokenByValueSerializer,
    RegionSerializer,
    SubregionSerializer,
    PartySerializer,
    PartyRatificationSerializer,
    ReportingPeriodSerializer,
    ObligationSerializer,
    UserSerializer,
    SubmissionSerializer,
    ListSubmissionSerializer,
    CreateSubmissionSerializer,
    Article7QuestionnaireSerializer,
    Article7DestructionSerializer,
    Article7ProductionSerializer,
    Article7ExportSerializer,
    Article7ImportSerializer,
    Article7NonPartyTradeSerializer,
    Article7EmissionSerializer,
    HighAmbientTemperatureProductionSerializer,
    HighAmbientTemperatureImportSerializer,
    DataOtherSerializer,
    GroupSerializer,
    SubstanceSerializer,
    BlendSerializer,
    CreateBlendSerializer,
    SubmissionHistorySerializer,
    SubmissionTransitionsSerializer,
    SubmissionInfoSerializer,
    UpdateSubmissionInfoSerializer,
    SubmissionFlagsSerializer,
    SubmissionRemarksSerializer,
    SubmissionFileSerializer,
    UploadTokenSerializer,
    ExemptionNominationSerializer,
    ExemptionApprovedSerializer,
    RAFSerializer,
    SubmissionFormatSerializer,
    AggregationSerializer,
    LimitSerializer,
)


from .export_pdf import export_submission


User = get_user_model()

log = logging.getLogger(__name__)


class ReadOnlyMixin:
    """Does what it says on the tin"""

    def _allowed_methods(self):
        return ['GET', 'OPTIONS']


class BulkCreateUpdateMixin:
    """
    Allows bulk creation and update of resources (given as a list in a JSON),
    while still permitting a single resource to be created.

    put() has been added as otherwise it is not available on the ViewSet. A
    concrete update() method needs to be implemented in the corresponding
    serializer.

    If the view receives a list of objects to be updated, get_object() returns
    a queryset referencing the existing objects corresponding to this
    submission. The (multiple-)update() implementation in the serializer needs
    to take this into account.

    This needs to be used by a `ModelViewSet` to properly work.
    """

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True

        return super().get_serializer(*args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def get_object(self):
        try:
            return super().get_object()
        except AssertionError:
            # If it's not one we return many!
            return self.get_queryset()


class IsOwnerFilterBackend(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        if not request.user.is_authenticated or request.user.is_anonymous:
            return queryset.none()
        elif request.user.is_secretariat:
            # Secretariat user
            return queryset
        else:
            # Party user
            if queryset is not None and queryset.model in (Submission, ProdCons, Limit):
                return queryset.filter(party=request.user.party)
            elif queryset is not None:
                return queryset.filter(submission__party=request.user.party)
            else:
                return queryset


class SerializerRequestContextMixIn(object):
    """Adds the current request to the serializer context."""

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class SerializerDataContextMixIn(SerializerRequestContextMixIn):
    """Adds the current submission to the serializer context."""

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if "submission_pk" in self.kwargs:
            context['submission'] = Submission.objects.get(
                pk=self.kwargs["submission_pk"]
            )
        return context


class CurrentUserViewSet(
    ReadOnlyMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
    mixins.ListModelMixin, GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = CurrentUserSerializer
    permission_classes = (IsAuthenticated, IsSecretariatOrSamePartyUser)

    def get_queryset(self):
        if self.kwargs.get('pk'):
            return self.queryset.filter(id=self.kwargs.get('pk'))
        else:
            return self.queryset.filter(id=self.request.user.pk)


class RegionViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = (IsAuthenticated,)


class SubregionViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = Subregion.objects.all()
    serializer_class = SubregionSerializer
    permission_classes = (IsAuthenticated,)


class PartyViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = Party.objects.all().prefetch_related(
        'subregion', 'subregion__region'
    )
    serializer_class = PartySerializer
    permission_classes = (IsAuthenticated,)


class PartyRatificationViewSet(ReadOnlyMixin, generics.ListAPIView):
    serializer_class = PartyRatificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Party.get_main_parties().prefetch_related(
            'subregion', 'ratifications', 'ratifications__treaty'
        )
        if self.kwargs.get('party_id'):
            queryset = queryset.filter(id=self.kwargs['party_id'])
        return queryset


class GetNonPartiesViewSet(ReadOnlyMixin, views.APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)

    def get(self, request, period_name):
        groups = Group.objects.all()
        all_non_parties = {}

        period = ReportingPeriod.objects.get(name=period_name) \
            if period_name else None

        for group in groups:
            queryset = group.get_non_parties(period)
            non_parties_per_group = {
                id: True for id in queryset.values_list('id', flat=True)
            }
            all_non_parties[group.group_id] = non_parties_per_group
        return Response(all_non_parties)


class ReportingPeriodViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = ReportingPeriod.objects.all()
    serializer_class = ReportingPeriodSerializer
    permission_classes = (IsAuthenticated,)


class ObligationViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = Obligation.objects.all()
    serializer_class = ObligationSerializer
    permission_classes = (IsAuthenticated,)


class GroupViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    """
    list:
    Get the list of substances grouped by their Group.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        serializer = GroupSerializer(
            self.filter_queryset(self.get_queryset()),
            many=True,
            context={"request": request},
        )

        data = deepcopy(serializer.data)
        data.append(
            OrderedDict(
                [
                    ('group_id', 'uncontrolled'),
                    (
                        'substances',
                        SubstanceSerializer(
                            Substance.objects.filter(group__isnull=True),
                            many=True,
                            read_only=True,
                            context={"request": request}
                        ).data
                    )
                ]
            )
        )
        return Response(data)


class BlendViewSet(viewsets.ModelViewSet):
    """
    list:
    Get the list of all non-custom blends, plus the custom ones that belongs
    to the user's party.
    """

    permission_classes = (IsAuthenticated, IsSecretariatOrSamePartyBlend, )

    def get_queryset(self):
        queryset = Blend.objects.all().prefetch_related(
            'components', 'components__substance'
        )
        party = self.request.user.party or self.request.query_params.get('party', None)
        if party is not None:
            queryset = queryset.filter(
                party=party) | queryset.filter(party=None)
        return queryset

    def get_serializer_class(self):
        if self.request.method in ["POST", "PUT", "PATCH"]:
            return CreateBlendSerializer
        return BlendSerializer


class UserViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)


class AggregationPaginator(PageNumberPagination):
    page_query_param = "page"
    page_size_query_param = "page_size"


class AggregationViewFilterSet(filters.FilterSet):
    party = filters.NumberFilter("party", help_text="Filter by party ID")
    reporting_period = filters.NumberFilter(
        "reporting_period", help_text="Filter by Reporting Period ID"
    )
    group = filters.NumberFilter(
        "group", help_text="Filter by Annex Group ID"
    )


class AggregationViewSet(viewsets.ModelViewSet):
    # Will only allow GET for now on this view
    http_method_names = ['get']

    queryset = ProdCons.objects.filter(party=F('party__parent_party'))
    serializer_class = AggregationSerializer

    filter_backends = (
        # Aggregations are public information, no need to enforce filtering
        # IsOwnerFilterBackend,
        filters.DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    )
    filterset_class = AggregationViewFilterSet
    search_fields = (
        "party__name", "reporting_period__name"
    )
    ordering_fields = {
        "party": "party",
        "reporting_period": "reporting_period",
        "group": "group",
    }
    ordering = ("-reporting_period", "party", "group")
    permission_classes = (
        IsAuthenticated, IsSecretariatOrSamePartyAggregation,
    )
    pagination_class = AggregationPaginator

    def get_queryset(self):
        return ProdCons.objects.filter(party=F('party__parent_party'))


class LimitPaginator(PageNumberPagination):
    page_query_param = "page"
    page_size_query_param = "page_size"


class LimitViewFilterSet(filters.FilterSet):
    party = filters.NumberFilter("party", help_text="Filter by party ID")
    reporting_period = filters.NumberFilter(
        "reporting_period", help_text="Filter by Reporting Period ID"
    )
    group = filters.NumberFilter(
        "group", help_text="Filter by Annex Group ID"
    )


class LimitViewSet(viewsets.ModelViewSet):
    # Will only allow GET for now on this view
    http_method_names = ['get']

    queryset = Limit.objects.filter(party=F('party__parent_party'))
    serializer_class = LimitSerializer

    filter_backends = (
        IsOwnerFilterBackend,
        filters.DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    )
    filterset_class = LimitViewFilterSet
    search_fields = (
        "party__name", "reporting_period__name"
    )
    ordering_fields = {
        "party": "party",
        "reporting_period": "reporting_period",
        "group": "group",
    }
    ordering = ("-reporting_period", "party", "group")
    permission_classes = (
        IsAuthenticated, IsSecretariatOrSamePartyLimit,
    )
    pagination_class = LimitPaginator

    def get_queryset(self):
        return Limit.objects.filter(party=F('party__parent_party'))


class SubmissionPaginator(PageNumberPagination):
    page_query_param = "page"
    page_size_query_param = "page_size"


class SubmissionViewFilterSet(filters.FilterSet):
    party = filters.NumberFilter("party", help_text="Filter by party ID")
    obligation = filters.NumberFilter(
        "obligation", help_text="Filter by Obligation ID"
    )
    reporting_period = filters.NumberFilter(
        "reporting_period", help_text="Filter by Reporting Period ID"
    )
    is_superseded = filters.BooleanFilter(
        method="filter_superseded",
        help_text="If set to true only show superseded submissions. "
                  "If set to false only show non-superseded submissions. "
    )
    from_period = filters.DateFilter(
        "reporting_period__start_date",
        "gte",
        help_text="Only get results for reporting periods that start "
        "at a later date than this.",
    )
    to_period = filters.DateFilter(
        "reporting_period__end_date",
        "lte",
        help_text="Only get results for reporting periods that end "
        "at a earlier date than this.",
    )
    current_state = filters.CharFilter(
        "_current_state", help_text="Filter by the submission state."
    )

    def filter_superseded(self, queryset, name, value):
        if value:
            return queryset.filter(flag_superseded=True)
        else:
            return queryset.exclude(flag_superseded=True)


class SubmissionViewSet(viewsets.ModelViewSet):
    """
    versions:
    Get a list of all submissions versions, including the one specified in the
    primary key.

    history:
    Get a list of all historical states for this specific submission version.
    Note historical states for other versions are not included.
    """
    queryset = Submission.objects.all().prefetch_related(
        "reporting_period", "created_by", "party"
    )
    filter_backends = (
        IsOwnerFilterBackend,
        filters.DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    )
    filterset_class = SubmissionViewFilterSet
    search_fields = (
        "party__name", "obligation__name", "reporting_period__name"
    )
    ordering_fields = {
        "obligation": "obligation",
        "party": "party",
        "reporting_period": "reporting_period",
        "version": "version",
        "_current_state": "current_state",
        "updated_at": "updated_at",
    }
    ordering = ("-reporting_period", "obligation")
    permission_classes = (IsAuthenticated, IsSecretariatOrSamePartySubmission, )
    pagination_class = SubmissionPaginator

    def get_queryset(self):
        return Submission.objects.all().prefetch_related(
            "reporting_period", "created_by", "party"
        )

    def update(self, *args, **kwargs):
        # Uses PartialUpdateMixIn to prevent race conditions
        # see https://github.com/encode/django-rest-framework/issues/2648
        kwargs["partial"] = True
        return super().update(*args, **kwargs)

    def get_serializer_class(self):
        if self.request.method in ["POST", "PUT", "PATCH"]:
            return CreateSubmissionSerializer
        return SubmissionSerializer

    def _list_submission(self, queryset, request):
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ListSubmissionSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = ListSubmissionSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        return self._list_submission(self.get_queryset(), request)

    @action(detail=True, methods=["get"])
    def versions(self, request, pk=None):
        return self._list_submission(
            Submission.objects.get(pk=pk).versions, request
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsSecretariatOrSamePartySubmissionClone]
    )
    def clone(self, request, pk=None):
        submission = Submission.objects.get(pk=pk)
        clone = submission.clone(request.user)
        return Response(
            {
                "url": reverse(
                    'core:submission-detail',
                    request=request,
                    kwargs={'pk': clone.id}
                )
            }
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="call-transition",
        permission_classes = [IsSecretariatOrSamePartySubmissionTransition]
    )
    def call_transition(self, request, pk=None):
        """
        Request example:
        {
            "transition": "submit"
        }
        """

        if request.data.get("transition"):
            submission = Submission.objects.get(pk=pk)
            submission.call_transition(request.data["transition"], request.user)
            serializer = SubmissionSerializer(
                submission, many=False, context={"request": request}
            )
            return Response(serializer.data)
        else:
            raise InvalidRequest(
                _(
                    "Invalid request: request body should contain 'transition' "
                    "key."
                )
            )

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        historical_records = Submission.objects.get(pk=pk).history.all()
        serializer = SubmissionHistorySerializer(historical_records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def export_pdf(self, request, pk=None):
        submission = Submission.objects.get(pk=pk)
        timestamp = datetime.now().strftime('%d-%m-%Y %H:%M')
        filename = f'submission_{pk}_{timestamp}.pdf'
        buf_pdf = export_submission(submission)
        resp = HttpResponse(buf_pdf, content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'
        return resp

    @action(detail=True, methods=["get"])
    def aggregations(self, request, submission_pk=None, pk=None):
        sub = Submission.objects.get(pk=pk)
        return Response(
            [
                AggregationSerializer(aggregation).data
                for group, aggregation in sub.get_aggregated_data().items()
            ]
        )


class SubmissionTransitionsViewSet(viewsets.ModelViewSet):
    form_types = None
    serializer_class = SubmissionTransitionsSerializer
    permission_classes = (
        IsAuthenticated, IsSecretariatOrSamePartySubmissionRelated,
        IsCorrectObligation,
    )
    filter_backends = (IsOwnerFilterBackend,)
    http_method_names = ['get']

    def get_queryset(self):
        return Submission.objects.filter(
            id=self.kwargs['submission_pk']
        )


class SubmissionInfoViewSet(viewsets.ModelViewSet):
    form_types = None
    serializer_class = SubmissionInfoSerializer
    permission_classes = (
        IsAuthenticated, IsSecretariatOrSamePartySubmissionRelated,
        IsCorrectObligation,
    )
    filter_backends = (IsOwnerFilterBackend,)
    http_method_names = ['get', 'put']

    def put(self, request, *args, **kwargs):
        info = Submission.objects.get(pk=self.kwargs['submission_pk']).info
        reporting_channel = request.data.get('reporting_channel')
        submitted_at = self.request.data.get('submitted_at')
        submission_format = request.data.get('submission_format')
        serializer = UpdateSubmissionInfoSerializer(
            info,
            data=request.data,
            context={
                'reporting_channel': reporting_channel,
                'submitted_at': submitted_at,
                'submission_format': submission_format,
                'request': request
            }
        )
        # Horrible hack to allow date to be an empty string
        if serializer.initial_data.get('date', None) == '':
            serializer.initial_data['date'] = None
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return SubmissionInfo.objects.filter(
            submission=self.kwargs['submission_pk']
        )


class GetSubmissionFormatsViewSet(ReadOnlyMixin, generics.ListAPIView):
    """
    retrieve:
    Get the available options for the submission format.
    """

    queryset = SubmissionFormat.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = SubmissionFormatSerializer


class SubmissionFlagsViewSet(
    mixins.UpdateModelMixin, mixins.ListModelMixin,
    GenericViewSet, SerializerRequestContextMixIn
):
    form_types = None
    serializer_class = SubmissionFlagsSerializer
    permission_classes = (
        IsAuthenticated, IsSecretariatOrSamePartySubmissionFlags,
        IsCorrectObligation,
    )
    filter_backends = (IsOwnerFilterBackend,)
    http_method_names = ['get', 'put']

    def put(self, request, *args, **kwargs):
        sub = Submission.objects.get(pk=self.kwargs['submission_pk'])
        # Uses PartialUpdateMixIn to prevent race conditions
        # see https://github.com/encode/django-rest-framework/issues/2648
        serializer = self.get_serializer(sub, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return Submission.objects.filter(
            pk=self.kwargs['submission_pk']
        )


class SubmissionRemarksViewSet(
    mixins.UpdateModelMixin, mixins.ListModelMixin,
    GenericViewSet, SerializerRequestContextMixIn
):
    """
    list:
    Get the general remarks for this specific submission. These are in pairs for
    each data form: remarks that have been added by the reporting party and remarks
    that have been added by the Ozone Secretariat.

    update:
    Update the general remarks for this specific submission.
    """
    # XXX TODO Check if this should be available for all #497
    form_types = None
    serializer_class = SubmissionRemarksSerializer
    permission_classes = (
        IsAuthenticated, IsSecretariatOrSamePartySubmissionRemarks,
        IsCorrectObligation,
    )
    filter_backends = (IsOwnerFilterBackend,)
    http_method_names = ['get', 'put']

    def put(self, request, *args, **kwargs):
        sub = Submission.objects.get(pk=self.kwargs['submission_pk'])
        # Uses PartialUpdateMixIn to prevent race conditions
        # see https://github.com/encode/django-rest-framework/issues/2648
        serializer = self.get_serializer(sub, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return Submission.objects.filter(
            pk=self.kwargs['submission_pk']
        )


class Article7QuestionnaireViewSet(viewsets.ModelViewSet):
    form_types = ("art7",)
    serializer_class = Article7QuestionnaireSerializer
    permission_classes = (
        IsAuthenticated, IsSecretariatOrSamePartySubmissionRelated,
        IsCorrectObligation,
    )
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return Article7Questionnaire.objects.filter(
            submission=self.kwargs['submission_pk']
        )

    def put(self, request, *args, **kwargs):
        article7questionnaire = Submission.objects.get(
            pk=self.kwargs['submission_pk']
        ).article7questionnaire
        serializer = Article7QuestionnaireSerializer(
            article7questionnaire, data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7DestructionViewSet(
    BulkCreateUpdateMixin, SerializerDataContextMixIn, viewsets.ModelViewSet
):
    form_types = ("art7",)
    serializer_class = Article7DestructionSerializer
    permission_classes = (
        IsAuthenticated, IsSecretariatOrSamePartySubmissionRelated,
        IsCorrectObligation,
    )
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return Article7Destruction.objects.filter(
            submission=self.kwargs['submission_pk']
        ).filter(blend_item__isnull=True)

    # Needed to ensure that serializer uses the correct submission
    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7ProductionViewSet(
    BulkCreateUpdateMixin, SerializerDataContextMixIn, viewsets.ModelViewSet
):
    form_types = ("art7",)
    serializer_class = Article7ProductionSerializer
    permission_classes = (
        IsAuthenticated, IsSecretariatOrSamePartySubmissionRelated,
        IsCorrectObligation,
    )
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return Article7Production.objects.filter(
            submission=self.kwargs['submission_pk']
        )

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7ExportViewSet(
    BulkCreateUpdateMixin, SerializerDataContextMixIn, viewsets.ModelViewSet
):
    form_types = ("art7",)
    serializer_class = Article7ExportSerializer
    permission_classes = (
        IsAuthenticated, IsSecretariatOrSamePartySubmissionRelated,
        IsCorrectObligation,
    )
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return Article7Export.objects.filter(
            submission=self.kwargs['submission_pk']
        ).filter(blend_item__isnull=True)

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7ImportViewSet(
    BulkCreateUpdateMixin, SerializerDataContextMixIn, viewsets.ModelViewSet
):
    form_types = ("art7",)
    serializer_class = Article7ImportSerializer
    permission_classes = (
        IsAuthenticated, IsSecretariatOrSamePartySubmissionRelated,
        IsCorrectObligation,
    )
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return Article7Import.objects.filter(
            submission=self.kwargs['submission_pk']
        ).filter(blend_item__isnull=True)

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7NonPartyTradeViewSet(
    BulkCreateUpdateMixin, SerializerDataContextMixIn, viewsets.ModelViewSet
):
    form_types = ("art7",)
    serializer_class = Article7NonPartyTradeSerializer
    permission_classes = (
        IsAuthenticated, IsSecretariatOrSamePartySubmissionRelated,
        IsCorrectObligation,
    )
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return Article7NonPartyTrade.objects.filter(
            submission=self.kwargs['submission_pk']
        ).filter(blend_item__isnull=True)

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7EmissionViewSet(
    BulkCreateUpdateMixin, SerializerDataContextMixIn, viewsets.ModelViewSet
):
    form_types = ("art7",)
    serializer_class = Article7EmissionSerializer
    permission_classes = (
        IsAuthenticated, IsSecretariatOrSamePartySubmissionRelated,
        IsCorrectObligation,
    )
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return Article7Emission.objects.filter(
            submission=self.kwargs['submission_pk']
        )

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class HighAmbientTemperatureImportViewSet(
    BulkCreateUpdateMixin, SerializerDataContextMixIn, viewsets.ModelViewSet
):
    form_types = ("hat",)
    serializer_class = HighAmbientTemperatureImportSerializer
    permission_classes = (
        IsAuthenticated, IsSecretariatOrSamePartySubmissionRelated,
        IsCorrectObligation,
    )
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return HighAmbientTemperatureImport.objects.filter(
            submission=self.kwargs['submission_pk']
        ).filter(blend_item__isnull=True)

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class HighAmbientTemperatureProductionViewSet(
    BulkCreateUpdateMixin, SerializerDataContextMixIn, viewsets.ModelViewSet
):
    form_types = ("hat",)
    serializer_class = HighAmbientTemperatureProductionSerializer
    permission_classes = (
        IsAuthenticated, IsSecretariatOrSamePartySubmissionRelated,
        IsCorrectObligation,
    )
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return HighAmbientTemperatureProduction.objects.filter(
            submission=self.kwargs['submission_pk']
        )

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class DataOtherViewSet(SerializerDataContextMixIn, viewsets.ModelViewSet):
    form_types = ("other",)
    serializer_class = DataOtherSerializer
    permission_classes = (
        IsAuthenticated, IsSecretariatOrSamePartySubmissionRelated,
        IsCorrectObligation,
    )
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return DataOther.objects.filter(
            submission=self.kwargs['submission_pk']
        )

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class ExemptionNominationViewSet(
    BulkCreateUpdateMixin, SerializerDataContextMixIn, viewsets.ModelViewSet
):
    form_types = ("exemption",)
    serializer_class = ExemptionNominationSerializer
    permission_classes = (
        IsAuthenticated, IsSecretariatOrSafeMethod, IsCorrectObligation,
    )
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return Nomination.objects.filter(
            submission=self.kwargs['submission_pk']
        )

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class ExemptionApprovedViewSet(
    BulkCreateUpdateMixin, SerializerDataContextMixIn, viewsets.ModelViewSet,
):
    form_types = ("exemption",)
    serializer_class = ExemptionApprovedSerializer
    permission_classes = (
        IsAuthenticated, IsSecretariatOrSafeMethod, IsCorrectObligation
    )
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return ExemptionApproved.objects.filter(
            submission=self.kwargs['submission_pk']
        )

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class RAFViewSet(
    BulkCreateUpdateMixin, SerializerDataContextMixIn, viewsets.ModelViewSet,
):
    form_types = ("essencrit",)
    serializer_class = RAFSerializer
    permission_classes = (
        IsAuthenticated, IsSecretariatOrSamePartySubmissionRelated,
        IsCorrectObligation,
    )
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return RAFReport.objects.filter(
            submission=self.kwargs['submission_pk']
        )


class SubmissionFileViewSet(BulkCreateUpdateMixin, viewsets.ModelViewSet):
    """
    download:
    Download the submission file.
    """
    form_types = None
    serializer_class = SubmissionFileSerializer
    permission_classes = (
        IsAuthenticated, IsSecretariatOrSamePartySubmissionRelated,
        IsCorrectObligation,
    )

    def get_queryset(self):
        return SubmissionFile.objects.filter(
            submission=self.kwargs['submission_pk']
        )

    @action(detail=True, methods=["get"])
    def download(self, request, submission_pk=None, pk=None):
        obj = self.get_object()
        if isinstance(obj, QuerySet):
            obj = obj.get(pk=pk)

        # We could try to guess the correct mime type here.
        response = HttpResponse(
            obj.file.read(), content_type="application/octet-stream"
        )
        file_name = urllib.parse.quote(obj.name)
        response['Content-Disposition'] = f"attachment; filename*=UTF-8''{file_name}; filename=\"{file_name}\""
        return response


class UploadHookViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    """
    Handles upload notifications for tusd hooks:
        - ``pre-create``
        - ``post-create``
        - ``post-finish``
        - ``post-terminate``
        - ``post-receive``
    tusd should be configured to point to the URL associated with this view.

    """
    @staticmethod
    def handle_pre_create(request):
        """
        Handles a pre-create notification from `tusd`.

        Sets the file name on the token.

        Returns an OK response only if:
         - the upload `token` the `MetaData` field is validated
         - the token's user is authenticated
         - a `filename` field is present in `MetaData`
        """
        log.info(f'UPLOAD pre-create: {request.data}')
        meta_data = request.data.get('MetaData', {})
        tok = meta_data.get('token', '')
        filename = meta_data.get('filename')
        try:
            token = UploadToken.objects.get(token=tok)

            if token.has_expired():
                token.delete()
                log.error('UPLOAD denied: EXPIRED TOKEN')
                return Response(
                    {'error': 'expired token'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not token.user.is_authenticated:
                log.error(
                    f'UPLOAD denied for "{token.user}": NOT ALLOWED'
                )
                return Response(
                    {'error': 'user not authenticated'},
                    status=status.HTTP_403_FORBIDDEN
                )

            if filename is None:
                log.error(f'UPLOAD denied for "{token.user}": filename missing')
                return Response(
                    {'error': 'filename not in MetaData'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not SubmissionFile.has_valid_extension(filename):
                log.error(
                    f'UPLOAD denied for "{token.user}": bad file extension'
                )
                return Response(
                    {'error': 'bad file extension'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token.filename = filename
            token.save()

            log.info(
                f'UPLOAD authorized for "{token.user}" '
                f'on submission {token.submission}'
            )

        except UploadToken.DoesNotExist:
            log.error('UPLOAD denied: INVALID TOKEN')
            return Response(
                {'error': 'invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response()

    @staticmethod
    def handle_post_receive(request):
        """
        Handles a post-receive notification from `tusd`.
        Currently has no side-effects, exists only to avoid
        'hook not implemented' errors in `tusd`.
        """
        log.info(f'UPLOAD post-receive: {request.data}')
        return Response()

    @staticmethod
    def handle_post_create(request):
        """
        Handles a post-create notification from `tusd`.
        Sets the newly issued tus ID on the token.
        """
        log.info(f'UPLOAD post-create: {request.data}')
        meta_data = request.data.get('MetaData', {})
        tok = meta_data.get('token', '')
        try:
            token = UploadToken.objects.get(token=tok)
            token.tus_id = request.data.get('ID')
            token.save()
        except UploadToken.DoesNotExist:
            log.error('UPLOAD denied: INVALID TOKEN')
            return Response(
                {'error': 'invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response()

    @staticmethod
    def handle_post_finish(request):
        """
        Handles a post-finish notification from `tusd`.
        The uploaded file is used to create an EnvelopeFile, or replace its
        underlying file on disk if one with the same name exists.
        """
        log.info(f'UPLOAD post-finish: {request.data}')
        meta_data = request.data.get('MetaData', {})
        tok = meta_data.get('token', '')
        description = meta_data.get('description', '')
        # filename presence was enforced during pre-create
        file_name = meta_data['filename']
        file_ext = file_name.split('.')[-1].lower()

        try:
            token = UploadToken.objects.get(token=tok)
            if not token.user.is_authenticated:
                log.error(f'UPLOAD denied for "{token.user}": NOT ALLOWED')
                return Response(
                    {'error': 'user not authenticated'},
                    status=status.HTTP_403_FORBIDDEN
                )

            upload_id = request.data.get('ID')

            submission_file = SubmissionFile.objects.create(
                submission=token.submission,
                name=file_name,
                uploader=token.user,
                tus_id=upload_id,
                description=description,
                upload_successful=False
            )

            file_path = os.path.join(
                settings.TUSD_UPLOADS_DIR,
                f'{upload_id}.bin'
            )
            file_info_path = os.path.join(
                settings.TUSD_UPLOADS_DIR,
                f'{upload_id}.info'
            )

            file_path = Path(file_path).resolve()
            file_info_path = Path(file_info_path).resolve()

            for f in (file_path, file_info_path):
                if not f.is_file():
                    raise FileNotFoundError(f'UPLOAD tusd file not found: {f}')

            log.info(f'file extension: {file_ext}')
            log.info(f'allowed extensions: {settings.ALLOWED_FILE_EXTENSIONS}')

            # At this point, submission_file.file_name is not necessarily
            # identical to the original file name
            submission_file.file.save(
                submission_file.name, File(file_path.open(mode='rb'))
            )
            submission_file.uploader = token.user
            submission_file.upload_successful = True
            submission_file.save()

            # Finally, remove the token and the tusd files pair
            token.delete()
            file_path.unlink()
            file_info_path.unlink()

        except UploadToken.DoesNotExist:
            log.error(f'UPLOAD denied for "{tok}": INVALID TOKEN')
            return Response(
                {'error': 'invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except FileNotFoundError as err:
            log.error(f'{err}')
            return Response(
                {'error': 'file not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response()

    @staticmethod
    def handle_post_terminate(request):
        """
        Handles a post-terminate notification from `tusd`.
        Deletes the token issued for the upload.
        """
        log.info(f'UPLOAD post-terminate: {request.data}')
        meta_data = request.data.get('MetaData', {})
        tok = meta_data.get('token', '')
        try:
            token = UploadToken.objects.get(token=tok)
            token.delete()
        except UploadToken.DoesNotExist:
            log.warning(
                'UPLOAD could not find token to delete on post-terminate.'
            )
        return Response()

    def create(self, request):
        """
        Dispatches notifications from `tusd` to appropriate handler.
        """
        # Original header name sent by tusd is `Hook-Name`, Django mangles it
        hook_name = self.request.META.get('HTTP_HOOK_NAME')
        try:
            hook_handler = getattr(
                self, f'handle_{hook_name.replace("-", "_")}'
            )
        except AttributeError:
            return Response(
                {'hook_not_supported': hook_name},
                status=status.HTTP_400_BAD_REQUEST
            )

        return hook_handler(request)


class UploadTokenViewSet(viewsets.ModelViewSet):
    queryset = UploadToken.objects.all()
    serializer_class = UploadTokenSerializer
    permission_classes = (
        IsAuthenticated, IsSecretariatOrSamePartySubmissionRelated,
    )

    def create(self, request, submission_pk):
        """
        Creates an ``UploadToken`` for the submission.
        Used by `tusd` uploads server for user/submission correlation.
        Upload tokens cannot be issued for non-editable submissions

        Returns::

            {
              'token': <base64 encoded token>
            }

        """
        submission = Submission.objects.get(pk=submission_pk)

        if not submission.can_upload_files(request.user):
            return Response(
                {
                    'error': _(
                        'You do not have permission to upload files for this submission'
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        token = submission.upload_tokens.create(user=request.user)
        response = {'token': token.token}

        # Include base64 encoded token in development environments
        if settings.DEBUG:
            response['token_base64'] = b64encode(token.token.encode())

        return Response(response)

    def list(self, request, submission_pk):
        """
        Returns the tokens issued for a given submission.
        """
        queryset = UploadToken.objects.filter(submission=submission_pk)
        serializer = self.serializer_class(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)


class AuthTokenViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    lookup_field = 'key'
    lookup_url_kwarg = 'token'
    serializer_class = AuthTokenByValueSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Token.objects.filter(user=self.request.user)
        else:
            return Token.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = AuthTokenSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        response = Response({'token': token.key})
        response.set_cookie("authToken", token.key)
        return response

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            user_token = Token.objects.get(user=request.user)
        except Token.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if user_token != instance:
            return Response(status=status.HTTP_404_NOT_FOUND)

        self.perform_destroy(instance)

        response = Response(status=status.HTTP_204_NO_CONTENT)
        if "_impersonate" in request.session:
            real_user = User.objects.get(pk=request.session["_auth_user_id"])
            stop_impersonate(request)
            # Set the token of the "real user", that has been impersonating
            # this user.
            token, created = Token.objects.get_or_create(user=real_user)
            response.set_cookie("authToken", token.key)
        else:
            # Also remove any active session.
            request.session.delete()
            response.delete_cookie("authToken")
        return response


class DefaultValuesViewSet(ReadOnlyMixin, views.APIView):
    """
    retrieve:
    Get the default values for 'Obligation' and 'Reporting Period'.
    """
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)

    def get(self, request):
        default_obligation_obj = Obligation.get_default()
        default_obligation = (
            default_obligation_obj.name
            if default_obligation_obj
            else None
        )

        default_reporting_period_obj = ReportingPeriod.get_most_recent()
        default_reporting_period = (
            default_reporting_period_obj.name
            if default_reporting_period_obj
            else None
        )

        default_reporting_channel_obj = ReportingChannel.get_default(
            request.user
        )
        default_reporting_channel = (
            default_reporting_channel_obj.name
            if default_reporting_channel_obj
            else None
        )

        default_submission_format_obj = SubmissionFormat.get_default(
            request.user
        )
        default_submission_format = (
            default_submission_format_obj.name
            if default_submission_format_obj
            else None
        )

        return Response({
            'obligation': default_obligation,
            'reporting_period': default_reporting_period,
            'reporting_channel': default_reporting_channel,
            'submission_format': default_submission_format,
        })
