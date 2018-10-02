from rest_framework import viewsets
from rest_framework.response import Response

from ozone.users.models import User

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
    UpdateSubmissionSerializer,
    Article7QuestionnaireSerializer,
    CreateArticle7QuestionnaireSerializer,
    Article7DestructionSerializer,
    CreateArticle7DestructionSerializer,
    Article7ProductionSerializer,
    CreateArticle7ProductionSerializer,
    Article7ExportSerializer,
    CreateArticle7ExportSerializer,
)


class ReadOnlyMixin:
    def _allowed_methods(self):
        return ['GET', 'OPTIONS']


class RegionViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer


class SubregionViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = Subregion.objects.all()
    serializer_class = SubregionSerializer


class PartyViewSet(ReadOnlyMixin, viewsets.ModelViewSet):
    queryset = Party.objects.all()
    serializer_class = PartySerializer


class ReportingPeriodViewSet(viewsets.ModelViewSet):
    queryset = ReportingPeriod.objects.all()
    serializer_class = ReportingPeriodSerializer


class ObligationViewSet(viewsets.ModelViewSet):
    queryset = Obligation.objects.all()
    serializer_class = ObligationSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateSubmissionSerializer
        if self.request.method in ["PUT", "PATCH"]:
            return UpdateSubmissionSerializer
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


class Article7DestructionViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Article7Destruction.objects.filter(
            submission=self.kwargs['submission_pk']
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateArticle7DestructionSerializer
        return Article7DestructionSerializer

    # Needed to ensure that serializer uses the correct submission
    def perform_create(self, serializer):
        serializer.save(submission_id=self.kwargs['submission_pk'])


class Article7ProductionViewSet(viewsets.ModelViewSet):
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


class Article7ExportViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Article7Export.objects.filter(
            submission=self.kwargs['submission_pk']
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateArticle7ExportSerializer
        return Article7ExportSerializer
