from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from rest_framework import viewsets, mixins, status, generics
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
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
    CreateArticle7DestructionSerializer,
    Article7ProductionSerializer,
    CreateArticle7ProductionSerializer,
    Article7ExportSerializer,
    CreateArticle7ExportSerializer,
    Article7ImportSerializer,
    CreateArticle7ImportSerializer,
    Article7NonPartyTradeSerializer,
    CreateArticle7NonPartyTradeSerializer,
    Article7EmissionSerializer,
    CreateArticle7EmissionSerializer,
    GroupSerializer,
    BlendSerializer,
    CreateBlendSerializer,
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


class BulkCreateMixin:
    """
    Allows bulk creation of resources (given as a list in a JSON),
    while still permitting a single resource to be created.
    """
    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True

        return super().get_serializer(*args, **kwargs)


class RegionViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer


class SubregionViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = Subregion.objects.all()
    serializer_class = SubregionSerializer


class PartyViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = Party.objects.all().prefetch_related('subregion')
    serializer_class = PartySerializer


class GetNonPartiesViewSet(generics.ListAPIView):
    serializer_class = PartySerializer

    def get_queryset(self):
        return Article7NonPartyTrade.get_non_parties(
            self.kwargs["substance_pk"]
        )


class ReportingPeriodViewSet(viewsets.ModelViewSet):
    queryset = ReportingPeriod.objects.all()
    serializer_class = ReportingPeriodSerializer


class ObligationViewSet(viewsets.ModelViewSet):
    queryset = Obligation.objects.all()
    serializer_class = ObligationSerializer


class GroupViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class BlendViewSet(viewsets.ModelViewSet):
    queryset = Blend.objects.all()

    def get_serializer_class(self):
        if self.request.method in ["POST", "PUT", "PATCH"]:
            return CreateBlendSerializer
        return BlendSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.custom is False:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.perform_update(instance)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()

    def get_serializer_class(self):
        if self.request.method in ["POST", "PUT", "PATCH"]:
            return CreateSubmissionSerializer
        return SubmissionSerializer

    def list(self, request, *args, **kwargs):
        serializer = ListSubmissionSerializer(
            self.queryset, many=True, context={'request': request}
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
    ValidationErrorMixin, BulkCreateMixin, viewsets.ModelViewSet
):
    def get_queryset(self):
        return Article7Destruction.objects.filter(
            submission=self.kwargs['submission_pk']
        ).filter(blend_item__isnull=True)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateArticle7DestructionSerializer
        return Article7DestructionSerializer

    # Needed to ensure that serializer uses the correct submission
    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7ProductionViewSet(
    ValidationErrorMixin, BulkCreateMixin, viewsets.ModelViewSet
):
    def get_queryset(self):
        return Article7Production.objects.filter(
            submission=self.kwargs['submission_pk']
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateArticle7ProductionSerializer
        return Article7ProductionSerializer

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7ExportViewSet(
    ValidationErrorMixin, BulkCreateMixin, viewsets.ModelViewSet
):
    def get_queryset(self):
        return Article7Export.objects.filter(
            submission=self.kwargs['submission_pk']
        ).filter(blend_item__isnull=True)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateArticle7ExportSerializer
        return Article7ExportSerializer

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7ImportViewSet(
    ValidationErrorMixin, BulkCreateMixin, viewsets.ModelViewSet
):
    def get_queryset(self):
        return Article7Import.objects.filter(
            submission=self.kwargs['submission_pk']
        ).filter(blend_item__isnull=True)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateArticle7ImportSerializer
        return Article7ImportSerializer

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7NonPartyTradeViewSet(
    ValidationErrorMixin, BulkCreateMixin, viewsets.ModelViewSet
):
    def get_queryset(self):
        return Article7NonPartyTrade.objects.filter(
            submission=self.kwargs['submission_pk']
        ).filter(blend_item__isnull=True)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateArticle7NonPartyTradeSerializer
        return Article7NonPartyTradeSerializer

    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7EmissionViewSet(
    ValidationErrorMixin, BulkCreateMixin, viewsets.ModelViewSet
):
    def get_queryset(self):
        return Article7Emission.objects.filter(
            submission=self.kwargs['submission_pk']
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateArticle7EmissionSerializer
        return Article7EmissionSerializer

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
