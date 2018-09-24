from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer

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


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('name', 'abbr')


class SubregionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subregion
        fields = ('name', 'abbr', 'region')


class PartySerializer(serializers.ModelSerializer):
    subregion = serializers.StringRelatedField(many=False)

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


class CreateArticle7QuestionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article7Questionnaire
        fields = '__all__'


class Article7DestructionSerializer(serializers.ModelSerializer):
    submission = serializers.PrimaryKeyRelatedField(
        read_only=True, many=False
    )
    substance = serializers.StringRelatedField(many=False, read_only=True)
    blend = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Article7Destruction
        fields = ('submission', 'substance', 'blend', 'quantity_destroyed',)


class CreateArticle7DestructionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article7Destruction
        fields = '__all__'


class SubmissionArticle7DestructionSerializer(
    NestedHyperlinkedModelSerializer,
    Article7DestructionSerializer
):
    parent_lookup_kwargs = {
        'submission_pk': 'submission__pk',
    }

    class Meta(Article7DestructionSerializer.Meta):
        fields = ('url',)
        extra_kwargs = {
            'url': {'view_name': 'core:submission-article7-destructions-detail'}
        }


class SubmissionSerializer(serializers.HyperlinkedModelSerializer):
    """
    This also needs to nested-serialize all data related to the specific
    submission.
    """
    party = serializers.StringRelatedField(many=False, read_only=True)
    reporting_period = serializers.StringRelatedField(
        many=False, read_only=True
    )
    obligation = serializers.StringRelatedField(
        many=False, read_only=True
    )

    # TODO: singular-ize this (inc. Model)
    # At most one questionnaire per emission, but multiple other data
    article7questionnaires = serializers.HyperlinkedIdentityField(
        many=False,
        read_only=True,
        view_name='core:submission-article7-questionnaire-list',
        lookup_url_kwarg='submission_pk'
    )

    article7destructions = SubmissionArticle7DestructionSerializer(
        many=True,
        read_only=True
    )
    created_by = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    last_edited_by = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Submission
        fields = ('id', 'party', 'reporting_period', 'version',
                  'article7questionnaires', 'article7destructions',
                  'created_by', 'last_edited_by', 'obligation')

# TODO: CreateSubmissionSerializer
