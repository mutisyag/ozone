from rest_framework import viewsets

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
)

from ..serializers import (
    RegionSerializer,
    SubregionSerializer,
    PartySerializer,
    ReportingPeriodSerializer,
    ObligationSerializer,
    UserSerializer,
    SubmissionSerializer,
    Article7QuestionnaireSerializer,
    Article7DestructionSerializer,
    CreateArticle7DestructionSerializer,
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
    serializer_class = SubmissionSerializer


class Article7QuestionnaireViewSet(viewsets.ModelViewSet):
    queryset = Article7Questionnaire.objects.all()

    serializer_class = Article7QuestionnaireSerializer


class Article7DestructionViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Article7Destruction.objects.filter(
            submission=self.kwargs['submission_pk']
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateArticle7DestructionSerializer
        return Article7DestructionSerializer
