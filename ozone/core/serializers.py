from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import (
    Region,
    Subregion,
    Party,
    ReportingPeriod,
    Obligation,
    Substance,
    Group,
    BlendComponent,
    Blend,
    Submission,
    Article7Questionnaire,
    Article7Destruction,
    Article7Production,
    Article7Export,
    Article7Import,
    Article7NonPartyTrade,
    Article7Emission,
)

User = get_user_model()


class BaseBulkUpdateSerializer(serializers.ListSerializer):
    """
    This is a base class for serializers that allow bulk updates (PUT requests
    containing a list of objects to create under a specific resource)
    """
    class ConfigurationError(Exception):
        pass

    # This needs to be set properly by each class inheriting from it
    substance_blend_fields = None

    def __init__(self, *args, **kwargs):
        if self.substance_blend_fields is None:
            raise self.ConfigurationError(
                'Class attribute `substance_blend_fields` needs to be non-empty'
            )
        if not isinstance(self.substance_blend_fields, list):
            raise self.ConfigurationError(
                'Class attribute `substance_blend_fields` needs to be a list'
            )

        super().__init__(*args, **kwargs)

    def update(self, instance, validated_data):
        """
        Updating data reports in a submission will work as follows:
        - all substances in queryset that do not appear in `validated_data`
          will be deleted.
        - substances in queryset that do appear in `validated_data` will be
          updated.
        - substances in `validated_data` that do not appear in queryset will
          have entries created for them

        The update method will *only permit lists* to be passed as parameters.
        The `instance` parameter is, in this case, a queryset!
        """
        submission = instance.first().submission

        # We will initiate to_delete list as the initial queryset, and then
        # gradually exclude from it based on the su
        to_delete = instance
        for field in self.substance_blend_fields:
            exclude_list = [
                data.get(field) for data in validated_data
                if data.get(field, None) is not None
            ]
            exclude_params={f'{field}__in': exclude_list}
            to_delete = to_delete.exclude(**exclude_params)
        # After all exclusions performed, delete
        to_delete.delete()

        # Now perform creations and updates; blend_item rows will
        # update automatically :)
        ret = []
        for data in validated_data:
            field_params = {
                field: data.pop(field, None)
                for field in self.substance_blend_fields
            }
            obj, created = instance.update_or_create(
                submission=submission,
                **field_params,
                defaults=data
            )
            ret.append(obj)

        return ret


class BaseBlendCompositionSerializer(serializers.ModelSerializer):
    """
    This will be used as a base for all reporting serializers that accept
    both substances and blends.
    """

    derived_substance_data = serializers.SerializerMethodField()

    def get_derived_substance_data(self, obj):
        derived_substances = []
        if obj.blend:
            for component in obj.components.all():
                component_details = dict()
                component_details['substance'] = component.substance.name
                for quantity in obj.QUANTITY_FIELDS:
                    component_details[quantity] = getattr(component, quantity)
                derived_substances.append(component_details)
        return derived_substances


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
        fields = ('id', 'name', 'abbr', 'subregion')


class SubstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Substance
        fields = ('id', 'name')


class GroupSerializer(serializers.ModelSerializer):
    substances = SubstanceSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = Group
        fields = ('group_id', 'substances')


class BlendComponentSerializer(serializers.ModelSerializer):
    substance_name = serializers.StringRelatedField(
        source='substance', many=False, read_only=True
    )

    class Meta:
        model = BlendComponent
        fields = ('substance', 'substance_name', 'percentage')


class BlendSerializer(serializers.ModelSerializer):
    components = BlendComponentSerializer(many=True)

    class Meta:
        model = Blend
        fields = ('id', 'blend_id', 'type', 'custom', 'components')


class CreateBlendSerializer(serializers.ModelSerializer):
    components = BlendComponentSerializer(many=True)

    class Meta:
        model = Blend
        exclude = ('custom',)

    def create(self, validated_data):
        components_data = validated_data.pop('components')
        blend = Blend.objects.create(custom=True, **validated_data)
        for component_data in components_data:
            BlendComponent.objects.create(blend=blend, **component_data)
        return blend

    def update(self, instance, validated_data):
        # TODO: a blend update also needs to trigger a recalculation of
        # derived substance fields in data reports.
        components_data = validated_data.pop('components')
        blend = super().update(instance, validated_data)

        # Delete all components that do not correspond to the substance data
        qs = BlendComponent.objects.filter(blend=instance)
        qs.exclude(
            substance__pk__in=[c.get('substance').pk for c in components_data]
        ).delete()

        # And create/update the new ones
        for component_data in components_data:
            BlendComponent.objects.update_or_create(
                blend=instance,
                substance=component_data.get('substance'),
                defaults={'percentage': component_data.get('percentage')}
            )

        return blend


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
        fields = ('id', 'username', 'email')


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


class Article7DestructionListSerializer(BaseBulkUpdateSerializer):
    substance_blend_fields = ['substance', 'blend']


class Article7DestructionSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = Article7DestructionListSerializer
        model = Article7Destruction
        exclude = ('submission',)


class Article7ProductionListSerializer(BaseBulkUpdateSerializer):
    substance_blend_fields = ['substance', ]


class Article7ProductionSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = Article7ProductionListSerializer
        model = Article7Production
        exclude = ('submission',)


class Article7ExportSerializer(BaseBlendCompositionSerializer):
    class Meta:
        model = Article7Export
        exclude = ('submission',)


class Article7ImportSerializer(BaseBlendCompositionSerializer):
    class Meta:
        model = Article7Import
        exclude = ('submission',)


class Article7NonPartyTradeSerializer(BaseBlendCompositionSerializer):
    class Meta:
        model = Article7NonPartyTrade
        exclude = ('submission',)


class Article7EmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article7Emission
        exclude = ('submission',)


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

    article7imports_url = serializers.HyperlinkedIdentityField(
        view_name='core:submission-article7-imports-list',
        lookup_url_kwarg='submission_pk'
    )
    article7imports = Article7ImportSerializer(
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

    updated_at = serializers.DateTimeField(format='%Y-%m-%d')
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
            'article7imports_url', 'article7imports',
            'article7nonpartytrades_url', 'article7nonpartytrades',
            'article7emissions_url', 'article7emissions',
            'updated_at', 'created_by', 'last_edited_by',
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

    def update(self, instance, validated_data):
        if 'last_edited_by' not in validated_data:
            validated_data['last_edited_by'] = self.context['request'].user
        return super().update(instance, validated_data)


class ListSubmissionSerializer(CreateSubmissionSerializer):
    updated_at = serializers.DateTimeField(format='%Y-%m-%d')

    class Meta(CreateSubmissionSerializer.Meta):
        fields = (
            ('url',)
            + CreateSubmissionSerializer.Meta.fields
            + ('version', 'updated_at')
        )
        extra_kwargs = {'url': {'view_name': 'core:submission-detail'}}


class AuthTokenByValueSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    expires = serializers.SerializerMethodField()

    class Meta:
        model = Token
        fields = ('token', 'created', 'expires')

    @staticmethod
    def get_token(obj):
        return obj.key

    @staticmethod
    def get_expires(obj):
        return obj.created + settings.TOKEN_EXPIRE_INTERVAL
