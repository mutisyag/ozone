from collections import OrderedDict
from copy import deepcopy

from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets, mixins, status, generics, views
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import action
from rest_framework.filters import BaseFilterBackend, OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.reverse import reverse

from ..exceptions import InvalidRequest, MethodNotAllowed

from ..models import (
    Region,
    Subregion,
    Party,
    ReportingPeriod,
    Obligation,
    Submission,
    SubmissionInfo,
    Article7Questionnaire,
    Article7Destruction,
    Article7Production,
    Article7Export,
    Article7Import,
    Article7NonPartyTrade,
    Article7Emission,
    HighAmbientTemperatureImport,
    Group,
    Substance,
    Blend,
    ReportingChannel,
)
from ..permissions import IsSecretariatOrSameParty
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
    HighAmbientTemperatureImportSerializer,
    GroupSerializer,
    SubstanceSerializer,
    BlendSerializer,
    CreateBlendSerializer,
    SubmissionHistorySerializer,
    SubmissionInfoSerializer,
    UpdateSubmissionInfoSerializer,
    SubmissionFlagsSerializer,
    SubmissionRemarksSerializer)

User = get_user_model()


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
            super().get_object()
        except AssertionError:
            # If it's not one we return many!
            return self.get_queryset()


class IsOwnerFilterBackend(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        if not request.user.is_authenticated or request.user.is_anonymous:
            return queryset.none()
        elif request.user.is_secretariat or request.user.is_superuser:
            # Secretariat user
            return queryset
        else:
            # Party user
            if queryset is not None and queryset.model == Submission:
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
        context['submission'] = Submission.objects.get(pk=self.kwargs["submission_pk"])
        return context


class CurrentUserViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CurrentUserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
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

    def get(self, request):
        groups = Group.objects.all()
        all_non_parties = {}
        for group in groups:
            queryset = Article7NonPartyTrade.get_non_parties(group.pk)
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
    permission_classes = (IsAuthenticated, IsSecretariatOrSameParty,)

    def get_queryset(self):
        queryset = Blend.objects.all().prefetch_related(
            'components', 'components__substance'
        )
        party = self.request.query_params.get('party', None)
        if party is not None:
            queryset = queryset.filter(
                party=party) | queryset.filter(party=None)
        return queryset

    def get_serializer_class(self):
        if self.request.method in ["POST", "PUT", "PATCH"]:
            return CreateBlendSerializer
        return BlendSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        # TODO Move validation on Blend model
        if instance.custom is False:
            raise MethodNotAllowed(
                _("Non custom blends cannot be modified.")
            )
        return super().update(request, *args, **kwargs)


class UserViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)


class SubmissionPaginator(PageNumberPagination):
    page_size = 10
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
    is_current = filters.BooleanFilter(
        method="filter_current",
        help_text="If set to true only show latest versions."
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

    def filter_current(self, queryset, name, value):
        if value:
            return queryset.exclude(flag_superseded=True)
        else:
            return queryset.filter(flag_superseded=True)


class SubmissionViewSet(viewsets.ModelViewSet):
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
    permission_classes = (IsAuthenticated, IsSecretariatOrSameParty)
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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
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

    @action(detail=True, methods=["post"])
    def clone(self, request, pk=None):
        submission = Submission.objects.get(pk=pk)
        clone = submission.clone(request.user)
        return Response(
            {"url": reverse('core:submission-detail', request=request, kwargs={'pk': clone.id})}
        )

    @action(detail=True, methods=["post"], url_path="call-transition")
    def call_transition(self, request, pk=None):
        if request.data.get("transition"):
            submission = Submission.objects.get(pk=pk)
            submission.call_transition(request.data["transition"], request.user)
            serializer = SubmissionSerializer(
                submission, many=False, context={"request": request}
            )
            return Response(serializer.data)
        else:
            raise InvalidRequest(
                _("Invalid request: request body should contain 'transition' key.")
            )

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        historical_records = Submission.objects.get(pk=pk).history.all()
        serializer = SubmissionHistorySerializer(historical_records, many=True)
        return Response(serializer.data)


class SubmissionInfoViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionInfoSerializer
    permission_classes = (IsAuthenticated, IsSecretariatOrSameParty,)
    filter_backends = (IsOwnerFilterBackend,)
    http_method_names = ['get', 'put']

    def put(self, request, *args, **kwargs):
        info = Submission.objects.get(pk=self.kwargs['submission_pk']).info
        reporting_channel_name = request.data.get('reporting_channel')
        if reporting_channel_name:
            reporting_channel_id = ReportingChannel.objects.get(
                name=reporting_channel_name
            ).pk
            request.data['reporting_channel'] = reporting_channel_id
        serializer = UpdateSubmissionInfoSerializer(info, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return SubmissionInfo.objects.filter(
            submission=self.kwargs['submission_pk']
        )


class SubmissionFlagsViewSet(viewsets.ModelViewSet, SerializerRequestContextMixIn):
    serializer_class = SubmissionFlagsSerializer
    permission_classes = (IsAuthenticated, IsSecretariatOrSameParty,)
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


class SubmissionRemarksViewSet(viewsets.ModelViewSet, SerializerRequestContextMixIn):
    serializer_class = SubmissionRemarksSerializer
    permission_classes = (IsAuthenticated, IsSecretariatOrSameParty,)
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
    serializer_class = Article7QuestionnaireSerializer
    permission_classes = (IsAuthenticated, IsSecretariatOrSameParty,)
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


class Article7DestructionViewSet(BulkCreateUpdateMixin, SerializerDataContextMixIn,
                                 viewsets.ModelViewSet):
    serializer_class = Article7DestructionSerializer
    permission_classes = (IsAuthenticated, IsSecretariatOrSameParty,)
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return Article7Destruction.objects.filter(
            submission=self.kwargs['submission_pk']
        ).filter(blend_item__isnull=True)

    # Needed to ensure that serializer uses the correct submission
    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7ProductionViewSet(BulkCreateUpdateMixin, SerializerDataContextMixIn,
                                viewsets.ModelViewSet):
    serializer_class = Article7ProductionSerializer
    permission_classes = (IsAuthenticated, IsSecretariatOrSameParty,)
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return Article7Production.objects.filter(
            submission=self.kwargs['submission_pk']
        )

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7ExportViewSet(BulkCreateUpdateMixin, SerializerDataContextMixIn,
                            viewsets.ModelViewSet):
    serializer_class = Article7ExportSerializer
    permission_classes = (IsAuthenticated, IsSecretariatOrSameParty,)
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return Article7Export.objects.filter(
            submission=self.kwargs['submission_pk']
        ).filter(blend_item__isnull=True)

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7ImportViewSet(BulkCreateUpdateMixin, SerializerDataContextMixIn,
                            viewsets.ModelViewSet):
    serializer_class = Article7ImportSerializer
    permission_classes = (IsAuthenticated, IsSecretariatOrSameParty,)
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return Article7Import.objects.filter(
            submission=self.kwargs['submission_pk']
        ).filter(blend_item__isnull=True)

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7NonPartyTradeViewSet(BulkCreateUpdateMixin, SerializerDataContextMixIn,
                                   viewsets.ModelViewSet):
    serializer_class = Article7NonPartyTradeSerializer
    permission_classes = (IsAuthenticated, IsSecretariatOrSameParty,)
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return Article7NonPartyTrade.objects.filter(
            submission=self.kwargs['submission_pk']
        ).filter(blend_item__isnull=True)

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7EmissionViewSet(BulkCreateUpdateMixin, SerializerDataContextMixIn,
                              viewsets.ModelViewSet):
    serializer_class = Article7EmissionSerializer
    permission_classes = (IsAuthenticated, IsSecretariatOrSameParty,)
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
    serializer_class = HighAmbientTemperatureImportSerializer
    permission_classes = (IsAuthenticated, IsSecretariatOrSameParty,)
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return HighAmbientTemperatureImport.objects.filter(
            submission=self.kwargs['submission_pk']
        ).filter(blend_item__isnull=True)

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


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
        return Response({'token': token.key})

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
        # Also remove any active session.
        request.session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
