from rest_framework import serializers
from rest_framework_nested.serializers import NestedHyperlinkedModelSerializer
from rest_framework.reverse import reverse

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
    class Meta:
        model = Article7Questionnaire
        exclude = ('submission',)


class CreateArticle7QuestionnaireSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        submission = Submission.objects.get(
            pk=validated_data.pop('submission_id')
        )

        questionnaire, created = Article7Questionnaire.objects.update_or_create(
            submission=submission,
            defaults=validated_data
        )
        return questionnaire

    class Meta:
        model = Article7Questionnaire
        exclude = ('submission',)


class Article7DestructionSerializer(serializers.ModelSerializer):
    substance = serializers.StringRelatedField(many=False, read_only=True)
    blend = serializers.StringRelatedField(many=False, read_only=True)
    blend_item = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Article7Destruction
        exclude = ('submission',)


class CreateArticle7DestructionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article7Destruction
        # TODO: create base class for these serializers
        exclude = ('submission', 'blend_item')


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
            'url': {
                'view_name': 'core:submission-article7-destructions-detail'
            }
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

    # At most one questionnaire per submission, but multiple other data
    article7questionnaire_url = serializers.HyperlinkedIdentityField(
        view_name='core:submission-article7-questionnaire-list',
        lookup_url_kwarg='submission_pk'
    )
    article7questionnaire = Article7QuestionnaireSerializer(
        many=False, read_only=True
    )

    # We want to add a URL for the destructions list
    article7destructions_url = serializers.HyperlinkedIdentityField(
        view_name='core:submission-article7-destructions-list',
        lookup_url_kwarg='submission_pk'
    )
    article7destructions = Article7DestructionSerializer(
        many=True, read_only=True
    )

    created_by = serializers.StringRelatedField(read_only=True)
    last_edited_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Submission

        fields = (
            'id', 'party', 'reporting_period', 'obligation', 'version',
            'article7questionnaire_url', 'article7questionnaire',
            'article7destructions_url', 'article7destructions',
            'created_by', 'last_edited_by',
        )

        read_only_fields = (
            'created_by', 'last_edited_by',
        )


class CreateSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ('party', 'reporting_period', 'obligation', 'version',
                  'created_by', 'last_edited_by',)

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


class ListSubmissionSerializer(CreateSubmissionSerializer):
    class Meta(CreateSubmissionSerializer.Meta):
        fields = ('url',) + CreateSubmissionSerializer.Meta.fields
        extra_kwargs = {'url': {'view_name': 'core:submission-detail'}}
