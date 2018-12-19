from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import (
    Region,
    Subregion,
    Party,
    PartyRatification,
    ReportingPeriod,
    Obligation,
    Substance,
    Group,
    BlendComponent,
    Blend,
    Submission,
    SubmissionInfo,
    Treaty,
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


class TreatySerializer(serializers.ModelSerializer):
    class Meta:
        model = Treaty
        fields = ('treaty_id', 'name')


class RatificationSerializer(serializers.ModelSerializer):
    treaty = TreatySerializer(
        many=False, read_only=True
    )

    class Meta:
        model = PartyRatification
        fields = (
            'treaty', 'ratification_type', 'ratification_date',
            'entry_into_force_date'
        )


class PartySerializer(serializers.ModelSerializer):
    subregion = serializers.StringRelatedField(many=False)

    class Meta:
        model = Party
        fields = ('id', 'name', 'abbr', 'subregion', 'parent_party')


class PartyRatificationSerializer(serializers.ModelSerializer):
    subregion = serializers.StringRelatedField(many=False)
    ratifications = RatificationSerializer(
        many=True, read_only=True
    )
    flags = serializers.SerializerMethodField()

    def get_flags(self, obj):
        current_history_entry = obj.history.get(
            reporting_period=ReportingPeriod.get_current_period()
        )
        return {
            field: getattr(current_history_entry, field)
            for field in (
                'is_eu_member', 'is_high_ambient_temperature', 'is_article5'
            )
        }

    class Meta:
        model = Party
        fields = (
            'id', 'name', 'abbr', 'subregion', 'ratifications', 'flags',
        )


class SubstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Substance
        fields = (
            'id', 'name', 'description', 'sort_order',
            'odp', 'formula', 'number_of_isomers', 'min_odp', 'max_odp',
            'is_qps', 'is_contained_in_polyols',
        )


class GroupSerializer(serializers.ModelSerializer):
    substances = SubstanceSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = Group
        fields = ('group_id', 'substances')


class BlendComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlendComponent
        fields = ('substance', 'component_name', 'percentage')


class BlendSerializer(serializers.ModelSerializer):
    components = BlendComponentSerializer(many=True)

    class Meta:
        model = Blend
        fields = (
            'id', 'blend_id', 'custom', 'is_qps', 'party', 'type',
            'other_names', 'composition', 'components', 'sort_order',
        )
        read_only_fields = ('custom', 'is_qps',)


class CreateBlendSerializer(BlendSerializer):
    components = BlendComponentSerializer(many=True)

    class Meta(BlendSerializer.Meta):
        pass

    def create(self, validated_data):
        components_data = validated_data.pop('components')
        blend = Blend.objects.create(**validated_data)
        for component_data in components_data:
            BlendComponent.objects.create(blend=blend, **component_data)
        return blend

    def update(self, instance, validated_data):
        components_data = validated_data.pop('components')
        blend = super().update(instance, validated_data)

        validated_mapping = {}
        for c in components_data:
            # Substance, if present always takes precedence over component_name,
            # as we may want to change the component_name for a specific subst
            if c.get('substance', None) is not None:
                validated_mapping[c.get('substance')] = c
            elif c.get('component_name', "") != "":
                validated_mapping[c.get('component_name')] = c

        # Delete all components that do not correspond to the new data
        # and update the modified ones
        for c in BlendComponent.objects.filter(blend=instance):
            if c.substance not in validated_mapping.keys():
                if c.component_name not in validated_mapping.keys():
                    c.delete()
                else:
                    # No substance, but component name in validated_data
                    component_data = validated_mapping.pop(c.component_name)
                    c.percentage=component_data.get('percentage')
                    c.save()
            else:
                # Substance in validated_data
                component_data = validated_mapping.pop(c.substance)
                c.component_name=component_data.get('component_name', "")
                c.percentage=component_data.get('percentage')
                c.save()

        # And now create the new ones
        for key, component in validated_mapping.items():
            BlendComponent.objects.create(blend=instance, **component)

        return blend


class ReportingPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportingPeriod
        fields = (
            'id', 'name', 'start_date', 'end_date',
            'is_reporting_allowed', 'is_reporting_open'
        )


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


class Article7DestructionListSerializer(BaseBulkUpdateSerializer):
    substance_blend_fields = ['substance', 'blend']
    unique_with = None


class Article7DestructionSerializer(serializers.ModelSerializer):
    group = serializers.CharField(
        source='substance.group.group_id', default='', read_only=True
    )

    class Meta:
        list_serializer_class = Article7DestructionListSerializer
        model = Article7Destruction
        exclude = ('submission', 'blend_item',)


class Article7ProductionListSerializer(BaseBulkUpdateSerializer):
    substance_blend_fields = ['substance', ]
    unique_with = None


class Article7ProductionSerializer(serializers.ModelSerializer):
    group = serializers.CharField(
        source='substance.group.group_id', default='', read_only=True
    )

    class Meta:
        list_serializer_class = Article7ProductionListSerializer
        model = Article7Production
        exclude = ('submission',)


class Article7ExportListSerializer(BaseBulkUpdateSerializer):
    substance_blend_fields = ['substance', 'blend']
    unique_with = 'destination_party'


class Article7ExportSerializer(BaseBlendCompositionSerializer):
    group = serializers.CharField(source='substance.group.group_id', default='',
                                  read_only=True)

    class Meta:
        list_serializer_class = Article7ExportListSerializer
        model = Article7Export
        exclude = ('submission', 'blend_item',)


class Article7ImportListSerializer(BaseBulkUpdateSerializer):
    substance_blend_fields = ['substance', 'blend']
    unique_with = 'source_party'


class Article7ImportSerializer(BaseBlendCompositionSerializer):
    group = serializers.CharField(
        source='substance.group.group_id', default='', read_only=True
    )

    class Meta:
        list_serializer_class = Article7ImportListSerializer
        model = Article7Import
        exclude = ('submission', 'blend_item',)


class Article7NonPartyTradeListSerializer(BaseBulkUpdateSerializer):
    substance_blend_fields = ['substance', 'blend']
    unique_with = 'trade_party'


class Article7NonPartyTradeSerializer(BaseBlendCompositionSerializer):
    group = serializers.CharField(
        source='substance.group.group_id', default='', read_only=True
    )

    class Meta:
        list_serializer_class = Article7NonPartyTradeListSerializer
        model = Article7NonPartyTrade
        exclude = ('submission', 'blend_item',)


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


class SubmissionInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionInfo
        fields = '__all__'


class SubmissionFlagsSerializer(serializers.ModelSerializer):
    """
    Specific serializer used to present all submission flags as a nested
    object, since this is easily usable by the frontend.
    """
    class Meta:
        model = Submission
        fields = (
            'flag_provisional', 'flag_valid', 'flag_superseded',
            'flag_checked_blanks', 'flag_has_blanks', 'flag_confirmed_blanks',
            'flag_has_reported_a1', 'flag_has_reported_a2',
            'flag_has_reported_b1', 'flag_has_reported_b2',
            'flag_has_reported_b3', 'flag_has_reported_c1',
            'flag_has_reported_c2', 'flag_has_reported_c3',
            'flag_has_reported_e', 'flag_has_reported_f',
        )


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

    article7productions_url = serializers.HyperlinkedIdentityField(
        view_name='core:submission-article7-productions-list',
        lookup_url_kwarg='submission_pk'
    )

    article7exports_url = serializers.HyperlinkedIdentityField(
        view_name='core:submission-article7-exports-list',
        lookup_url_kwarg='submission_pk'
    )

    article7imports_url = serializers.HyperlinkedIdentityField(
        view_name='core:submission-article7-imports-list',
        lookup_url_kwarg='submission_pk'
    )

    article7nonpartytrades_url = serializers.HyperlinkedIdentityField(
        view_name='core:submission-article7-nonpartytrades-list',
        lookup_url_kwarg='submission_pk'
    )

    article7emissions_url = serializers.HyperlinkedIdentityField(
        view_name='core:submission-article7-emissions-list',
        lookup_url_kwarg='submission_pk'
    )

    sub_info_url = serializers.HyperlinkedIdentityField(
        view_name='core:submission-submission-info-list',
        lookup_url_kwarg='submission_pk',
    )
    sub_info = SubmissionInfoSerializer(
        many=False, read_only=True, source='info'
    )

    submission_flags_url = serializers.HyperlinkedIdentityField(
        view_name='core:submission-submission-flags-list',
        lookup_url_kwarg='submission_pk',
    )

    available_transitions = serializers.SerializerMethodField()
    is_cloneable = serializers.SerializerMethodField()
    changeable_flags = serializers.SerializerMethodField()

    updated_at = serializers.DateTimeField(format='%Y-%m-%d')
    created_by = serializers.StringRelatedField(read_only=True)
    last_edited_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Submission

        fields = (
            'id', 'party', 'reporting_period', 'obligation', 'version',
            'article7questionnaire_url', 'article7questionnaire',
            'article7destructions_url', 'article7productions_url',
            'article7exports_url', 'article7imports_url',
            'article7nonpartytrades_url', 'article7emissions_url',
            'sub_info_url', 'sub_info',
            'submission_flags_url',
            'updated_at', 'created_by', 'last_edited_by',
            'current_state', 'previous_state', 'available_transitions',
            'data_changes_allowed', 'is_current', 'is_cloneable',
            'changeable_flags',  'flag_provisional', 'flag_valid',
            'flag_superseded',
        )

        read_only_fields = (
            'created_by', 'last_edited_by',
        )

    def get_available_transitions(self, obj):
        user = self.context['request'].user
        return obj.available_transitions(user)

    def get_is_cloneable(self, obj):
        user = self.context['request'].user
        return obj.is_cloneable(user)

    def get_changeable_flags(self, obj):
        user = self.context['request'].user
        return obj.get_changeable_flags(user)


class CreateSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = (
            'id', 'party', 'reporting_period', 'obligation',
        )

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
    available_transitions = serializers.SerializerMethodField()
    is_cloneable = serializers.SerializerMethodField()

    class Meta(CreateSubmissionSerializer.Meta):
        fields = (
            ('url',)
            + CreateSubmissionSerializer.Meta.fields
            + (
                'created_at', 'updated_at', 'created_by', 'last_edited_by',
                'version', 'current_state', 'previous_state',
                'available_transitions', 'data_changes_allowed', 'is_current',
                'is_cloneable',
            )
        )
        extra_kwargs = {'url': {'view_name': 'core:submission-detail'}}

    def get_available_transitions(self, obj):
        user = self.context['request'].user
        return obj.available_transitions(user)

    def get_is_cloneable(self, obj):
        user = self.context['request'].user
        return obj.is_cloneable(user)


class SubmissionHistorySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    current_state = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = (
            'user', 'date', 'current_state',
            'flag_provisional', 'flag_valid', 'flag_superseded',
            'flag_checked_blanks', 'flag_has_blanks', 'flag_confirmed_blanks',
            'flag_has_reported_a1', 'flag_has_reported_a2',
            'flag_has_reported_b1', 'flag_has_reported_b2',
            'flag_has_reported_b3', 'flag_has_reported_c1',
            'flag_has_reported_c2', 'flag_has_reported_c3',
            'flag_has_reported_e', 'flag_has_reported_f',
        )

    def get_date(self, obj):
        return obj.history_date.strftime('%Y-%m-%d')

    def get_current_state(self, obj):
        # Unfortunately I can't find a way to avoid using the protected field
        return obj._current_state

    def get_user(self, obj):
        return obj.history_user.username


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
