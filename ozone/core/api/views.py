from collections import OrderedDict
from copy import deepcopy

from django.contrib.auth import get_user_model
from django.db.models import F
from django_filters import rest_framework as filters
from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets, mixins, status, generics, views
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import action
from rest_framework.filters import BaseFilterBackend
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

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
    Group,
    Substance,
    Blend,
)
from ..permissions import IsSecretariatOrSameParty
from ..serializers import (
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
    CreateArticle7QuestionnaireSerializer,
    Article7DestructionSerializer,
    Article7ProductionSerializer,
    Article7ExportSerializer,
    Article7ImportSerializer,
    Article7NonPartyTradeSerializer,
    Article7EmissionSerializer,
    GroupSerializer,
    SubstanceSerializer,
    BlendSerializer,
    CreateBlendSerializer,
    SubmissionHistorySerializer,
    SubmissionInfoSerializer,
)


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
            if queryset and queryset.model == Submission:
                return queryset.filter(party=request.user.party)
            elif queryset:
                return queryset.filter(submission__party=request.user.party)
            else:
                return queryset


class RegionViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = (IsAuthenticated,)


class SubregionViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = Subregion.objects.all()
    serializer_class = SubregionSerializer
    permission_classes = (IsAuthenticated,)


class PartyViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = Party.objects.all().prefetch_related('subregion')
    serializer_class = PartySerializer
    permission_classes = (IsAuthenticated,)


class PartyRatificationViewSet(ReadOnlyMixin, generics.ListAPIView):
    serializer_class = PartyRatificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Party.objects.filter(
            id=F('parent_party_id')
        ).prefetch_related('subregion').prefetch_related('ratifications')
        if self.kwargs.get('party_id'):
            queryset = queryset.filter(id=self.kwargs['party_id'])
        return queryset


class GetNonPartiesViewSet(ReadOnlyMixin, views.APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer, )

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
    permission_classes = (IsAuthenticated,)

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


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    filter_backends = (IsOwnerFilterBackend, filters.DjangoFilterBackend,)
    filter_fields = ('obligation', 'party', 'reporting_period',)
    permission_classes = (IsAuthenticated, IsSecretariatOrSameParty,)

    def get_queryset(self):
        return Submission.objects.all()

    def get_serializer_class(self):
        if self.request.method in ["POST", "PUT", "PATCH"]:
            return CreateSubmissionSerializer
        return SubmissionSerializer

    def list(self, request, *args, **kwargs):
        serializer = ListSubmissionSerializer(
            self.filter_queryset(self.get_queryset()),
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def clone(self, request, pk=None):
        submission = Submission.objects.get(pk=pk)
        clone = submission.clone()
        return Response({'id': clone.id})

    @action(detail=True, methods=['post'], url_path='call-transition')
    def call_transition(self, request, pk=None):
        if request.data.get('transition'):
            submission = Submission.objects.get(pk=pk)
            submission.call_transition(request.data['transition'])
            serializer = SubmissionSerializer(
                submission,
                many=False,
                context={"request": request}
            )
            return Response(serializer.data)
        else:
            raise InvalidRequest(
                _("Invalid request: request body should contain 'transition' key.")
            )

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        historical_records = Submission.objects.get(pk=pk).history.all()
        serializer = SubmissionHistorySerializer(
            historical_records, many=True
        )
        return Response(serializer.data)


class SubmissionInfoViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionInfoSerializer
    permission_classes = (IsAuthenticated, IsSecretariatOrSameParty,)
    filter_backends = (IsOwnerFilterBackend,)
    http_method_names = ['get', 'put']

    def get_queryset(self):
        return SubmissionInfo.objects.filter(
            submission=self.kwargs['submission_pk']
        )

class Article7QuestionnaireViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, IsSecretariatOrSameParty,)
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return Article7Questionnaire.objects.filter(
            submission=self.kwargs['submission_pk']
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateArticle7QuestionnaireSerializer
        return Article7QuestionnaireSerializer

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7DestructionViewSet(BulkCreateUpdateMixin, viewsets.ModelViewSet):
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


class Article7ProductionViewSet(BulkCreateUpdateMixin, viewsets.ModelViewSet):
    serializer_class = Article7ProductionSerializer
    permission_classes = (IsAuthenticated, IsSecretariatOrSameParty,)
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return Article7Production.objects.filter(
            submission=self.kwargs['submission_pk']
        )

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7ExportViewSet(BulkCreateUpdateMixin, viewsets.ModelViewSet):
    serializer_class = Article7ExportSerializer
    permission_classes = (IsAuthenticated, IsSecretariatOrSameParty,)
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return Article7Export.objects.filter(
            submission=self.kwargs['submission_pk']
        ).filter(blend_item__isnull=True)

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7ImportViewSet(BulkCreateUpdateMixin, viewsets.ModelViewSet):
    serializer_class = Article7ImportSerializer
    permission_classes = (IsAuthenticated, IsSecretariatOrSameParty,)
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return Article7Import.objects.filter(
            submission=self.kwargs['submission_pk']
        ).filter(blend_item__isnull=True)

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7NonPartyTradeViewSet(BulkCreateUpdateMixin, viewsets.ModelViewSet):
    serializer_class = Article7NonPartyTradeSerializer
    permission_classes = (IsAuthenticated, IsSecretariatOrSameParty,)
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return Article7NonPartyTrade.objects.filter(
            submission=self.kwargs['submission_pk']
        ).filter(blend_item__isnull=True)

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7EmissionViewSet(BulkCreateUpdateMixin, viewsets.ModelViewSet):
    serializer_class = Article7EmissionSerializer
    permission_classes = (IsAuthenticated, IsSecretariatOrSameParty,)
    filter_backends = (IsOwnerFilterBackend,)

    def get_queryset(self):
        return Article7Emission.objects.filter(
            submission=self.kwargs['submission_pk']
        )

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class AuthTokenViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):

    lookup_field = 'key'
    lookup_url_kwarg = 'token'
    serializer_class = AuthTokenByValueSerializer
    permission_classes = (AllowAny, )

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Token.objects.filter(user=self.request.user)
        else:
            return Token.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = AuthTokenSerializer(data=request.data,
                                         context={'request': request})
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
        return Response(status=status.HTTP_204_NO_CONTENT)
