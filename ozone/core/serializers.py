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
    Article7Destruction,
    Article7Production,
    Article7Export,
    Article7NonPartyTrade,
    Article7Emission
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


class Article7ProductionSerializer(serializers.ModelSerializer):
    substance = serializers.StringRelatedField(many=False, read_only=True)
    decision = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Article7Production
        exclude = ('submission',)


class CreateArticle7ProductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article7Production
        exclude = ('submission',)


class SubmissionArticle7ProductionSerializer(
    NestedHyperlinkedModelSerializer,
    Article7ProductionSerializer
):
    parent_lookup_kwargs = {
        'submission_pk': 'submission__pk',
    }

    class Meta(Article7ProductionSerializer.Meta):
        fields = ('url',)
        extra_kwargs = {
            'url': {
                'view_name': 'core:submission-article7-productions-detail'
            }
        }


class Article7ExportSerializer(serializers.ModelSerializer):
    substance = serializers.StringRelatedField(many=False, read_only=True)
    blend = serializers.StringRelatedField(many=False, read_only=True)
    blend_item = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Article7Export
        exclude = ('submission',)


class CreateArticle7ExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article7Export
        exclude = ('submission', 'blend_item')


class SubmissionArticle7ExportSerializer(
    NestedHyperlinkedModelSerializer,
    Article7ExportSerializer
):
    parent_lookup_kwargs = {
        'submission_pk': 'submission__pk',
    }

    class Meta(Article7ExportSerializer.Meta):
        fields = ('url',)
        extra_kwargs = {
            'url': {
                'view_name': 'core:submission-article7-exports-detail'
            }
        }


class Article7NonPartyTradeSerializer(serializers.ModelSerializer):
    substance = serializers.StringRelatedField(many=False, read_only=True)
    blend = serializers.StringRelatedField(many=False, read_only=True)
    blend_item = serializers.StringRelatedField(many=False, read_only=True)
    trade_party = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Article7NonPartyTrade
        exclude = ('submission',)


class CreateArticle7NonPartyTradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article7NonPartyTrade
        exclude = ('submission', 'blend_item')


class SubmissionArticle7NonPartyTradeSerializer(
    NestedHyperlinkedModelSerializer,
    Article7NonPartyTradeSerializer
):
    parent_lookup_kwargs = {
        'submission_pk': 'submission__pk',
    }

    class Meta(Article7NonPartyTradeSerializer.Meta):
        fields = ('url',)
        extra_kwargs = {
            'url': {
                'view_name': 'core:submission-article7-nonpartytrades-detail'
            }
        }


class Article7EmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article7Emission
        exclude = ('submission',)


class CreateArticle7EmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article7Emission
        exclude = ('submission',)


class SubmissionArticle7EmissionSerializer(
    NestedHyperlinkedModelSerializer,
    Article7EmissionSerializer
):
    parent_lookup_kwargs = {
        'submission_pk': 'submission__pk',
    }

    class Meta(Article7EmissionSerializer.Meta):
        fields = ('url',)
        extra_kwargs = {
            'url': {
                'view_name': 'core:submission-article7-emissions-detail'
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

    article7productions_url = serializers.HyperlinkedIdentityField(
        view_name='core:submission-article7-productions-list',
        lookup_url_kwarg='submission_pk'
    )
    article7productions = Article7ProductionSerializer(
        many=True, read_only=True
    )

    article7exports_url = serializers.HyperlinkedIdentityField(
        view_name='core:submission-article7-exports-list',
        lookup_url_kwarg='submission_pk'
    )
    article7exports = Article7ExportSerializer(
        many=True, read_only=True
    )

    article7nonpartytrades_url = serializers.HyperlinkedIdentityField(
        view_name='core:submission-article7-nonpartytrades-list',
        lookup_url_kwarg='submission_pk'
    )
    article7nonpartytrades = Article7NonPartyTradeSerializer(
        many=True, read_only=True
    )

    article7emissions_url = serializers.HyperlinkedIdentityField(
        view_name='core:submission-article7-emissions-list',
        lookup_url_kwarg='submission_pk'
    )
    article7emissions = Article7EmissionSerializer(
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
            'article7productions_url', 'article7productions',
            'article7exports_url', 'article7exports',
            'article7nonpartytrades_url', 'article7nonpartytrades',
            'article7emissions_url', 'article7emissions',
            'created_by', 'last_edited_by',
        )

        read_only_fields = (
            'created_by', 'last_edited_by',
        )


class CreateSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ('party', 'reporting_period', 'obligation',)

    def create(self, validated_data):
        if 'created_by' not in validated_data:
            validated_data['created_by'] = self.context['request'].user
        if 'last_edited_by' not in validated_data:
            validated_data['last_edited_by'] = self.context['request'].user

        return super().create(validated_data)


class UpdateSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ('party', 'reporting_period', 'obligation',)

    def update(self, instance, validated_data):
        if 'last_edited_by' not in validated_data:
            validated_data['last_edited_by'] = self.context['request'].user
        return super().update(instance, validated_data)


class ListSubmissionSerializer(CreateSubmissionSerializer):
    class Meta(CreateSubmissionSerializer.Meta):
        fields = ('url',) + CreateSubmissionSerializer.Meta.fields + ('version',)
        extra_kwargs = {'url': {'view_name': 'core:submission-detail'}}
