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

    # These need to be set properly by each class that extends this
    # Fields in substance_blend_fields list are mutually exclusive (one DB entry
    # cannot have more that one of them not null (e.g. substance or blend))
    substance_blend_fields = None
    unique_with = None

    def __init__(self, *args, **kwargs):
        if not isinstance(self.substance_blend_fields, list):
            raise self.ConfigurationError(
                'Class attribute `substance_blend_fields` needs to be a list'
            )

        super().__init__(*args, **kwargs)

    def construct_data_dictionary(self, validated_data):
        """
        Constructs a dictionary with (substance, party) keys starting from
        validated_data (which is a list of data entries).
        This is later used to easily lookup existing entries and see if they
        need to be deleted or updated.
        This approach does not generate key collisions because
        `entry.get(field)` returns either a `Blend` or a `Substance` object,
        instead of integer id's.
        """
        if self.unique_with is None:
            data_dictionary = {
                entry.get(field): entry
                for entry in validated_data
                for field in self.substance_blend_fields
                if entry.get(field, None) is not None
            }
        else:
            data_dictionary = {
                (entry.get(field), entry.get(self.unique_with)): entry
                for entry in validated_data
                for field in self.substance_blend_fields
                if entry.get(field, None) is not None
            }
        return data_dictionary

    def construct_key(self, existing_entry):
        # These fields are mutually exclusive, so this works
        for field in self.substance_blend_fields:
            field_value = getattr(existing_entry, field)
            if field_value:
                # Construct key to find existing_entry in validated_data
                key = field_value
                if self.unique_with is not None:
                    key = (key, getattr(existing_entry, self.unique_with))
                return key
        # Should never get here
        return None

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
        # List of updated/created items to be returned
        ret = []

        data_dictionary = self.construct_data_dictionary(validated_data)

        if not data_dictionary:
            # If the data dictionary is not populated (e.g. there are no fields
            # to do lookups on), we simply delete all existing data
            instance.delete()
            data_dictionary = dict(enumerate(validated_data))
        else:
            # Hitting the database (one query) to iterate over the list of
            # existing data is a small price to pay for potentially avoiding
            # a lot of unnecessary updates afterwards (e.g. when a single record
            # changes for an existing submission with a lot of records).
            for existing_entry in instance:
                # Construct the key to lookup the existing entry in data_dict
                key = self.construct_key(existing_entry)

                # If existing entry needs to be deleted, delete it
                if key not in data_dictionary:
                    existing_entry.delete()
                # If it needs to be updated, update it and remove the
                # corresponding entry from validated_data
                else:
                    # Check if it needs to be updated to avoid database hit
                    entry = data_dictionary.pop(key)
                    changed = False
                    for field, value in entry.items():
                        if getattr(existing_entry, field, None) != value:
                            setattr(existing_entry, field, value)
                            changed = True
                    if changed:
                        existing_entry.save()
                        ret.append(existing_entry)

        # After all that is done, just create the entries that still need to be
        # created (have not been popped out of data_dictionary)
        for key, data in data_dictionary.items():
            obj = instance.create(
                submission=submission,
                **data
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
        fields = ('id', 'name', 'abbr', 'subregion', 'parent_party')


class SubstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Substance
        fields = ('id', 'name', 'description', 'sort_order')


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
        fields = ('substance', 'substance_name', 'component_name', 'percentage')


class BlendSerializer(serializers.ModelSerializer):
    components = BlendComponentSerializer(many=True)

    class Meta:
        model = Blend
        fields = ('id', 'blend_id', 'custom', 'party', 'type', 'components')


class CreateBlendSerializer(serializers.ModelSerializer):
    components = BlendComponentSerializer(many=True)

    class Meta:
        model = Blend
        fields = '__all__'

    def create(self, validated_data):
        components_data = validated_data.pop('components')
        blend = Blend.objects.create(**validated_data)
        for component_data in components_data:
            BlendComponent.objects.create(blend=blend, **component_data)
        return blend

    def update(self, instance, validated_data):
        # TODO: a blend update also needs to trigger a recalculation of
        # derived substance fields in data reports.
        components_data = validated_data.pop('components')
        blend = super().update(instance, validated_data)

        # Delete all components that do not correspond to the new data
        component_keys = [
            (c.get('substance', None), c.get('component_name', None))
            for c in components_data
        ]
        for c in BlendComponent.objects.filter(blend=instance):
            if (c.substance, c.component_name) not in component_keys:
                c.delete()

        # And create/update the new ones
        for component_data in components_data:
            BlendComponent.objects.update_or_create(
                blend=instance,
                substance=component_data.get('substance'),
                component_name=component_data.get('component_name'),
                defaults={'percentage': component_data.get('percentage')}
            )

        return blend


class ReportingPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportingPeriod
        fields = ('id', 'name', 'start_date', 'end_date', 'is_year')


class ObligationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Obligation
        fields = ('id', 'name', 'form_type')


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
    unique_with = None


class Article7DestructionSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = Article7DestructionListSerializer
        model = Article7Destruction
        exclude = ('submission',)


class Article7ProductionListSerializer(BaseBulkUpdateSerializer):
    substance_blend_fields = ['substance', ]
    unique_with = None


class Article7ProductionSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = Article7ProductionListSerializer
        model = Article7Production
        exclude = ('submission',)


class Article7ExportListSerializer(BaseBulkUpdateSerializer):
    substance_blend_fields = ['substance', 'blend']
    unique_with = 'destination_party'


class Article7ExportSerializer(BaseBlendCompositionSerializer):
    class Meta:
        list_serializer_class = Article7ExportListSerializer
        model = Article7Export
        exclude = ('submission',)


class Article7ImportListSerializer(BaseBulkUpdateSerializer):
    substance_blend_fields = ['substance', 'blend']
    unique_with = 'source_party'


class Article7ImportSerializer(BaseBlendCompositionSerializer):
    class Meta:
        list_serializer_class = Article7ImportListSerializer
        model = Article7Import
        exclude = ('submission',)


class Article7NonPartyTradeListSerializer(BaseBulkUpdateSerializer):
    substance_blend_fields = ['substance', 'blend']
    unique_with = 'trade_party'


class Article7NonPartyTradeSerializer(BaseBlendCompositionSerializer):
    class Meta:
        list_serializer_class = Article7NonPartyTradeListSerializer
        model = Article7NonPartyTrade
        exclude = ('submission',)


class Article7EmissionListSerializer(BaseBulkUpdateSerializer):
    """
    The list serializer for emissions needs to delete everything
    there was and create all data fresh, as there is no field to filter on.

    This is accomplished easily by setting substance_blend_fields = []
    """
    substance_blend_fields = []


class Article7EmissionSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = Article7EmissionListSerializer
        model = Article7Emission
        exclude = ('submission',)


class SubmissionSerializer(serializers.HyperlinkedModelSerializer):
    """
    This also needs to nested-serialize all data related to the specific
    submission.
    """
    party = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
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
            'current_state', 'previous_state', 'available_transitions',
            'data_changes_allowed', 'is_current'
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
    created_at = serializers.DateTimeField(format='%Y-%m-%d')
    updated_at = serializers.DateTimeField(format='%Y-%m-%d')

    class Meta(CreateSubmissionSerializer.Meta):
        fields = (
            ('url',)
            + CreateSubmissionSerializer.Meta.fields
            + (
                'created_at', 'updated_at', 'created_by', 'last_edited_by',
                'version', 'current_state', 'previous_state',
                'available_transitions', 'data_changes_allowed', 'is_current',
            )
        )
        extra_kwargs = {'url': {'view_name': 'core:submission-detail'}}


class SubmissionHistorySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    current_state = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = (
            'user', 'date', 'current_state',
            'flag_provisional', 'flag_valid', 'flag_superseded',
        )

    def get_date(self, obj):
        return obj.history_date.strftime('%Y-%m-%d')

    def get_current_state(self, obj):
        # Unfortunately I can't find a way to avoid using the protected field
        return obj._current_state

    def get_user(self, obj):
        if obj.history_user:
            return obj.history_user.username
        return None


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
