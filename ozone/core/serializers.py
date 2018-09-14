from rest_framework.exceptions import ValidationError
from rest_framework import serializers

from ozone.users.models import User
from .models import (
    Region,
    Subregion,
    Party,
    ReportingPeriod,
    Obligation,
    Submission,
    Article7Questionnaire,
    Article7Destruction
)


class RegionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Region
        fields = ('name', 'abbr')


class SubregionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Subregion
        fields = ('name', 'abbr', 'region')


class PartySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Party
        fields = ('name', 'abbr', 'subregion')


class ReportingPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportingPeriod
        fields = ('id', 'name', 'start_date', 'end_date')


class ObligationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Obligation
        fields = ('id', 'name')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email')


class Article7QuestionnaireSerializer(serializers.ModelSerializer):
    submission = serializers.PrimaryKeyRelatedField(
        read_only=True, many=False
    )

    class Meta:
        model = Article7Questionnaire
        fields = '__all__'


class Article7DestructionSerializer(serializers.ModelSerializer):
    submission = serializers.PrimaryKeyRelatedField(
        read_only=True, many=False
    )

    class Meta:
        model = Article7Destruction
        fields = '__all__'


class CreateArticle7DestructionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article7Destruction
        fields = '__all__'


class SubmissionSerializer(serializers.ModelSerializer):
    """
    This also needs to nested-serialize all data related to the specific
    submission.
    """
    # At most one questionnaire per emission, but multiple other data
    article7questionnaires = Article7QuestionnaireSerializer(
        many=False, read_only=True
    )
    article7destructions = Article7DestructionSerializer(
        many=True, read_only=True
    )
    #created_by = serializers.PrimaryKeyRelatedField(
    #    many=False, queryset=User.objects.all(), default=serializers.CurrentUserDefault()
    #)
    #last_edited_by = serializers.PrimaryKeyRelatedField(
    #    many=False, queryset=User.objects.all(), default=serializers.CurrentUserDefault()
    #)

    class Meta:
        model = Submission
        fields = ('id', 'party', 'reporting_period', 'version',
                  'article7questionnaires', 'article7destructions',
                  'created_by', 'last_edited_by', 'obligation')
