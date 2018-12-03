from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_filters import rest_framework as filters

from rest_framework import viewsets, mixins, status, generics
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ozone.core.serializers import AuthTokenByValueSerializer

from ..models import (
    Region,
    Subregion,
    Party,
    ReportingPeriod,
    Obligation,
    Submission,
    Article7Questionnaire,
    Article7Destruction,
    Article7Production,
    Article7Export,
    Article7Import,
    Article7NonPartyTrade,
    Article7Emission,
    Group,
    Blend,
)
from ..permissions import IsSecretariatOrSameParty
from ..serializers import (
    RegionSerializer,
    SubregionSerializer,
    PartySerializer,
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
    BlendSerializer,
    CreateBlendSerializer,
    SubmissionHistorySerializer,
)


User = get_user_model()


class ReadOnlyMixin:
    """Does what it says on the tin"""
    def _allowed_methods(self):
        return ['GET', 'OPTIONS']


class ValidationErrorMixin:
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response(
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                data=e.messages
            )


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


class RegionViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer


class SubregionViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = Subregion.objects.all()
    serializer_class = SubregionSerializer


class PartyViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = Party.objects.all().prefetch_related('subregion')
    serializer_class = PartySerializer


class GetNonPartiesViewSet(ReadOnlyMixin, generics.ListAPIView):
    serializer_class = PartySerializer

    def get_queryset(self):
        return Article7NonPartyTrade.get_non_parties(
            self.kwargs["substance_pk"]
        )


class ReportingPeriodViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = ReportingPeriod.objects.all()
    serializer_class = ReportingPeriodSerializer


class ObligationViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = Obligation.objects.all()
    serializer_class = ObligationSerializer


class GroupViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class BlendViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        queryset = Blend.objects.all().prefetch_related(
            'components', 'components__substance'
        )
        party = self.request.query_params.get('party', None)
        if party is not None:
            queryset = queryset.filter(party=party) | queryset.filter(party=None)
        return queryset

    def get_serializer_class(self):
        if self.request.method in ["POST", "PUT", "PATCH"]:
            return CreateBlendSerializer
        return BlendSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.custom is False:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)


class UserViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('obligation', 'party', 'reporting_period',)
    permission_classes = (IsAuthenticated, IsSecretariatOrSameParty,)

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated or user.is_anonymous:
            return Submission.objects.none()
        elif user.is_secretariat:
            # Secretariat user
            return Submission.objects.all()
        else:
            # Party user
            return Submission.objects.filter(party=user.party)

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

    def create(self, request, *args, **kwargs):
        if request.user.is_secretariat is False:
            party = Party.objects.get(pk=request.data.get('party', None))
            if party != request.user.party:
                return Response(status=status.HTTP_403_FORBIDDEN)
        super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def clone(self, request, pk=None):
        submission = Submission.objects.get(pk=pk)
        try:
            clone = submission.clone()
            return Response({'id': clone.id})
        except ValidationError as e:
            return Response(
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                data=e.messages
            )

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
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        historical_records = Submission.objects.get(pk=pk).history.all()
        serializer = SubmissionHistorySerializer(
            historical_records, many=True
        )
        return Response(serializer.data)


class Article7QuestionnaireViewSet(viewsets.ModelViewSet):
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


class Article7DestructionViewSet(
    ValidationErrorMixin, BulkCreateUpdateMixin, viewsets.ModelViewSet
):
    serializer_class = Article7DestructionSerializer

    def get_queryset(self):
        return Article7Destruction.objects.filter(
            submission=self.kwargs['submission_pk']
        ).filter(blend_item__isnull=True)

    # Needed to ensure that serializer uses the correct submission
    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7ProductionViewSet(
    ValidationErrorMixin, BulkCreateUpdateMixin, viewsets.ModelViewSet
):
    serializer_class = Article7ProductionSerializer

    def get_queryset(self):
        return Article7Production.objects.filter(
            submission=self.kwargs['submission_pk']
        )

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7ExportViewSet(
    ValidationErrorMixin, BulkCreateUpdateMixin, viewsets.ModelViewSet
):
    serializer_class = Article7ExportSerializer

    def get_queryset(self):
        return Article7Export.objects.filter(
            submission=self.kwargs['submission_pk']
        ).filter(blend_item__isnull=True)

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7ImportViewSet(
    ValidationErrorMixin, BulkCreateUpdateMixin, viewsets.ModelViewSet
):
    serializer_class = Article7ImportSerializer

    def get_queryset(self):
        return Article7Import.objects.filter(
            submission=self.kwargs['submission_pk']
        ).filter(blend_item__isnull=True)

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7NonPartyTradeViewSet(
    ValidationErrorMixin, BulkCreateUpdateMixin, viewsets.ModelViewSet
):
    serializer_class = Article7NonPartyTradeSerializer

    def get_queryset(self):
        return Article7NonPartyTrade.objects.filter(
            submission=self.kwargs['submission_pk']
        ).filter(blend_item__isnull=True)

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7EmissionViewSet(
    ValidationErrorMixin, BulkCreateUpdateMixin, viewsets.ModelViewSet
):
    serializer_class = Article7EmissionSerializer

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
