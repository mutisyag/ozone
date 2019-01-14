from copy import deepcopy

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta
from rest_framework_extensions.serializers import PartialUpdateSerializerMixin

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
    HighAmbientTemperatureProduction,
    DataOther,
    SubmissionFile,
    UploadToken,
    HighAmbientTemperatureImport,
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

    def update_single(self, existing_entry, entry):
        """Updates a single entry"""
        changed = False
        for field, value in entry.items():
            if getattr(existing_entry, field, None) != value:
                setattr(existing_entry, field, value)
                changed = True
        return changed

    def create_single(self, data, instance, submission):
        """Creates a single entry"""
        obj = instance.create(
            submission=submission,
            **data
        )
        return obj

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
                    if self.update_single(existing_entry, entry):
                        ret.append(existing_entry)

        for existing_entry in ret:
            existing_entry.save()

        # After all that is done, just create the entries that still need to be
        # created (have not been popped out of data_dictionary)
        for key, data in data_dictionary.items():
            obj = self.create_single(data, instance, submission)
            ret.append(obj)

        return ret


class CurrentUserSerializer(serializers.ModelSerializer):
    """
    Used to get basic info for current user
    """

    class Meta:
        model = User
        fields = ('username', 'is_secretariat', 'is_read_only', 'party',)


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


class DataCheckRemarksMixInBase(object):
    """Base class for checking remarks permissions for data entry."""

    def check_remarks(self, remark_party_changed, remark_os_changed):
        """Check if the party/secretariat remark are being incorrectly changed.

        Raises a ValidationError.
        """
        user = self.context['request'].user
        submission = self.context['submission']

        # XXX Logic duplicated in Submission.check_remarks
        if not submission.filled_by_secretariat and user.is_secretariat and remark_party_changed:
            # Secretariat users cannot modify any of the party fields, if the
            # submission was filled by a party.
            raise ValidationError({
                "remarks_party": [_('User is not allowed to change this remark')]
            })
        elif not user.is_secretariat and remark_os_changed:
            # Party users cannot modify any of the secretariat remark fields
            raise ValidationError({
                "remarks_os": [_('User is not allowed to change this remark')]
            })


class DataCheckRemarksMixIn(DataCheckRemarksMixInBase):
    """Check create and update permissions on remarks for adding/updating a single
    data entry.
    """

    def create(self, validated_data):
        if not isinstance(validated_data, list):
            self.check_remarks(
                bool(validated_data.get("remarks_party")),
                bool(validated_data.get("remarks_os"))
            )
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if not isinstance(validated_data, list):
            self.check_remarks(
                "remarks_party" in validated_data and validated_data["remarks_party"] != instance.remarks_party,
                "remarks_os" in validated_data and validated_data["remarks_os"] != instance.remarks_os
            )
        return super().update(instance, validated_data)


class DataCheckRemarksBulkUpdateMixIn(DataCheckRemarksMixIn):
    """Check create and update permissions on remarks for adding/updating bulk
    data entries.
    """

    def update_single(self, existing_entry, entry):
        self.check_remarks(
            "remarks_party" in entry and entry["remarks_party"] != existing_entry.remarks_party,
            "remarks_os" in entry and entry["remarks_os"] != existing_entry.remarks_os
        )
        return super().update_single(existing_entry, entry)

    def create_single(self, data, instance, submission):
        self.check_remarks(
            bool(data.get("remarks_party")),
            bool(data.get("remarks_os"))
        )
        return super().create_single(data, instance, submission)


class Article7DestructionListSerializer(DataCheckRemarksBulkUpdateMixIn, BaseBulkUpdateSerializer):
    substance_blend_fields = ['substance', 'blend']
    unique_with = None


class Article7DestructionSerializer(DataCheckRemarksMixIn, serializers.ModelSerializer):
    group = serializers.CharField(
        source='substance.group.group_id', default='', read_only=True
    )

    class Meta:
        list_serializer_class = Article7DestructionListSerializer
        model = Article7Destruction
        exclude = ('submission', 'blend_item',)


class Article7ProductionListSerializer(DataCheckRemarksBulkUpdateMixIn, BaseBulkUpdateSerializer):
    substance_blend_fields = ['substance', ]
    unique_with = None


class Article7ProductionSerializer(DataCheckRemarksMixIn, serializers.ModelSerializer):
    group = serializers.CharField(
        source='substance.group.group_id', default='', read_only=True
    )

    class Meta:
        list_serializer_class = Article7ProductionListSerializer
        model = Article7Production
        exclude = ('submission',)


def validate_import_export_data(
    initial_data, totals_fields, quantity_fields, party_field
):
    """
    Function for validation of initial data sent to the Import/Export
    serializers in regards to complex, per-form validation criteria
    (see https://github.com/eaudeweb/ozone/issues/81)
    """

    # Find all entries in self.initial_data that do not have a src/dst country
    # (actually, there should only be one such entry, but this cannot be
    # guaranteed at this stage of the request processing).
    # Then find all substances relating to those entries (could be blends)
    related_substances = []
    for entry in initial_data:
        if entry.get('party_field', None) is None:
            if entry.get('substance', None):
                related_substances.append(entry.get('substance'))
            elif entry.get('blend', None):
                related_substances.extend(
                    Blend.objects.get(
                        id=entry.get('blend')
                    )
                        .get_substance_ids()
                )

    # Calculate the sums of quantities and totals for each substance
    if related_substances:
        sums_dictionary = {
            substance: {'totals_sum': 0, 'quantities_sum': 0}
            for substance in related_substances
        }
        for entry in initial_data:
            if entry.get('blend', None):
                # Blend entry
                blend_subs = Blend.objects.get(
                    id=entry.get('blend')
                ).get_substance_ids_percentages()

                for substance, percentage in blend_subs:
                    if substance in related_substances:
                        sums_dictionary[substance]['totals_sum'] += sum(
                            [
                                entry.get(field, 0) * percentage
                                for field in totals_fields
                            ]
                        )
                        sums_dictionary[substance]['quantities_sum'] += sum(
                            [
                                entry.get(field, 0) * percentage
                                for field in quantity_fields
                            ]
                        )

            elif entry.get('substance', None):
                substance = entry.get('substance')
                sums_dictionary[substance]['totals_sum'] += sum(
                    [
                        entry.get(field, 0) for field in totals_fields
                    ]
                )
                sums_dictionary[substance]['quantities_sum'] += sum(
                    [
                        entry.get(field, 0) for field in quantity_fields
                    ]
                )

        # And finally verify that, for each substance,
        # sum of totals > sum of quantities
        valid = all(
            [
                sums['totals_sum'] >= sums['quantities_sum']
                for sums in sums_dictionary.values()
            ]
        )
        if not valid:
            raise ValidationError(
                'For each substance that has no destination_party,'
                'the sum of quantities across all data entries should be '
                'less than the sum of totals'
            )


class Article7ExportListSerializer(DataCheckRemarksBulkUpdateMixIn, BaseBulkUpdateSerializer):
    substance_blend_fields = ['substance', 'blend']
    unique_with = 'destination_party'

    def is_valid(self, raise_exception=False):
        """
        Overriding the serializer's default is_valid method so we add extra
        validation related to feedstock vs new/recovered quantities.

        Typically, such validations would be performed on the models, but in
        our case:
        - we need to import legacy data that might not satisfy these conditions
        - we need to perform the validation on a list of entries (i.e. model
        instances), aggregating data from several of them. That happens because
        we have bulk serializers.

        """
        # Call is_valid first to avoid expensive computation on invalid data
        ret = super().is_valid(raise_exception)

        totals_fields = ['quantity_total_new', 'quantity_total_recovered']
        quantity_fields = [
            f for f in Article7Export.QUANTITY_FIELDS
            if f not in totals_fields and f != 'quantity_polyols'
        ]

        # This will simply raise a ValidationError if self.initial_data does
        # not satisfy the totals >= quantities criteria.
        validate_import_export_data(
            self.initial_data, totals_fields, quantity_fields, self.unique_with
        )

        return ret


class Article7ExportSerializer(DataCheckRemarksMixIn, BaseBlendCompositionSerializer):
    group = serializers.CharField(source='substance.group.group_id', default='',
                                  read_only=True)

    class Meta:
        list_serializer_class = Article7ExportListSerializer
        model = Article7Export
        exclude = ('submission', 'blend_item',)


class Article7ImportListSerializer(DataCheckRemarksBulkUpdateMixIn, BaseBulkUpdateSerializer):
    substance_blend_fields = ['substance', 'blend']
    unique_with = 'source_party'

    def is_valid(self, raise_exception=False):
        """
        Overriding the serializer's default is_valid method so we add extra
        validation related to feedstock vs new/recovered quantities.

        Typically, such validations would be performed on the models, but in
        our case:
        - we need to import legacy data that might not satisfy these conditions
        - we need to perform the validation on a list of entries (i.e. model
        instances), aggregating data from several of them. That happens because
        we have bulk serializers.

        """
        # Call is_valid first to avoid expensive computation on invalid data
        ret = super().is_valid(raise_exception)

        totals_fields = ['quantity_total_new', 'quantity_total_recovered']
        quantity_fields = [
            f for f in Article7Import.QUANTITY_FIELDS
            if f not in totals_fields and f != 'quantity_polyols'
        ]

        # This will simply raise a ValidationError if self.initial_data does
        # not satisfy the totals >= quantities criteria.
        validate_import_export_data(
            self.initial_data, totals_fields, quantity_fields, self.unique_with
        )

        return ret


class Article7ImportSerializer(DataCheckRemarksMixIn, BaseBlendCompositionSerializer):
    group = serializers.CharField(
        source='substance.group.group_id', default='', read_only=True
    )

    class Meta:
        list_serializer_class = Article7ImportListSerializer
        model = Article7Import
        exclude = ('submission', 'blend_item',)


class Article7NonPartyTradeListSerializer(DataCheckRemarksBulkUpdateMixIn, BaseBulkUpdateSerializer):
    substance_blend_fields = ['substance', 'blend']
    unique_with = 'trade_party'


class Article7NonPartyTradeSerializer(DataCheckRemarksMixIn, BaseBlendCompositionSerializer):
    group = serializers.CharField(
        source='substance.group.group_id', default='', read_only=True
    )

    class Meta:
        list_serializer_class = Article7NonPartyTradeListSerializer
        model = Article7NonPartyTrade
        exclude = ('submission', 'blend_item',)


class Article7EmissionListSerializer(DataCheckRemarksBulkUpdateMixIn, BaseBulkUpdateSerializer):
    """
    The list serializer for emissions needs to delete everything
    there was and create all data fresh, as there is no field to filter on.

    This is accomplished easily by setting substance_blend_fields = []
    """
    substance_blend_fields = []


class Article7EmissionSerializer(DataCheckRemarksMixIn, serializers.ModelSerializer):
    class Meta:
        list_serializer_class = Article7EmissionListSerializer
        model = Article7Emission
        exclude = ('submission',)


class HighAmbientTemperatureProductionListSerializer(DataCheckRemarksBulkUpdateMixIn,
                                                     BaseBulkUpdateSerializer):
    substance_blend_fields = ['substance', ]
    unique_with = None


class HighAmbientTemperatureProductionSerializer(DataCheckRemarksMixIn, serializers.ModelSerializer):
    group = serializers.CharField(
        source='substance.group.group_id', default='', read_only=True
    )

    class Meta:
        list_serializer_class = HighAmbientTemperatureProductionListSerializer
        model = HighAmbientTemperatureProduction
        exclude = ('submission',)


class HighAmbientTemperatureImportListSerializer(DataCheckRemarksBulkUpdateMixIn,
                                                 BaseBulkUpdateSerializer):
    substance_blend_fields = ['substance', 'blend']
    unique_with = None


class HighAmbientTemperatureImportSerializer(DataCheckRemarksMixIn,
                                             BaseBlendCompositionSerializer):
    group = serializers.CharField(
        source='substance.group.group_id', default='', read_only=True
    )

    class Meta:
        list_serializer_class = HighAmbientTemperatureImportListSerializer
        model = HighAmbientTemperatureImport
        exclude = ('submission', 'blend_item',)


class DataOtherSerializer(DataCheckRemarksMixIn, serializers.ModelSerializer):
    class Meta:
        model = DataOther
        exclude = ('submission',)


class UpdateSubmissionInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubmissionInfo
        exclude = ('submission',)


class SubmissionInfoSerializer(serializers.ModelSerializer):
    reporting_channel = serializers.SerializerMethodField()

    class Meta:
        model = SubmissionInfo
        exclude = ('submission',)

    def get_reporting_channel(self, obj):
        return getattr(obj.reporting_channel, 'name', '')


class SubmissionFlagsSerializer(PartialUpdateSerializerMixin, serializers.ModelSerializer):
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
        
    def update(self, instance, validated_data):
        """
        Not really kosher to perform validations here, but we need to
        pass the user to the validation method in the model.
        Cannot override the serializer's validate() method either since it
        does not have access to the object instance.
        """
        # User should always be on the request due to our permission classes
        user = self.context['request'].user
        instance.check_flags(user, validated_data)
        return super().update(instance, validated_data)


class SubmissionRemarksSerializer(PartialUpdateSerializerMixin, serializers.ModelSerializer):
    """
    Specific serializer used to present all submission remarks,
    since this is easily usable by the frontend.
    """

    class Meta:
        model = Submission
        fields = (
            'imports_remarks_party', 'imports_remarks_secretariat',
            'exports_remarks_party', 'exports_remarks_secretariat',
            'production_remarks_party', 'production_remarks_secretariat',
            'destruction_remarks_party', 'destruction_remarks_secretariat',
            'nonparty_remarks_party', 'nonparty_remarks_secretariat',
            'emissions_remarks_party', 'emissions_remarks_secretariat',
            'hat_imports_remarks_party', 'hat_imports_remarks_secretariat',
            'hat_production_remarks_party', 'hat_production_remarks_secretariat',
        )

    def update(self, instance, validated_data):
        """
        Not really kosher to perform validations here, but we need to
        pass the user to the validation method in the model.
        Cannot override the serializer's validate() method either since it
        does not have access to the object instance.
        """
        # User should always be on the request due to our permission classes
        user = self.context['request'].user
        instance.check_remarks(user, validated_data)
        return super().update(instance, validated_data)


class SubmissionFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionFile
        fields = '__all__'


class UploadTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadToken
        fields = '__all__'


class SubmissionSerializer(PartialUpdateSerializerMixin, serializers.HyperlinkedModelSerializer):
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

    files = SubmissionFileSerializer(
        many=True, read_only=True
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

    hat_productions_url = serializers.HyperlinkedIdentityField(
        view_name='core:submission-hat-productions-list',
        lookup_url_kwarg='submission_pk'
    )

    hat_imports_url = serializers.HyperlinkedIdentityField(
        view_name='core:submission-hat-imports-list',
        lookup_url_kwarg='submission_pk',
    )

    data_others_url = serializers.HyperlinkedIdentityField(
        view_name='core:submission-data-others-list',
        lookup_url_kwarg='submission_pk'
    )

    files_url = serializers.HyperlinkedIdentityField(
        view_name='core:submission-files-list',
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
    submission_remarks = serializers.HyperlinkedIdentityField(
        view_name='core:submission-submission-remarks-list',
        lookup_url_kwarg='submission_pk',
    )

    available_transitions = serializers.SerializerMethodField()
    is_cloneable = serializers.SerializerMethodField()
    changeable_flags = serializers.SerializerMethodField()

    updated_at = serializers.DateTimeField(format='%Y-%m-%d')
    created_by = serializers.StringRelatedField(read_only=True)
    last_edited_by = serializers.StringRelatedField(read_only=True)

    can_change_remarks_party = serializers.SerializerMethodField()
    can_change_remarks_secretariat = serializers.SerializerMethodField()

    class Meta:
        model = Submission

        fields = (
            'id', 'party', 'reporting_period', 'obligation', 'version',
            'article7questionnaire_url', 'article7questionnaire',
            'article7destructions_url', 'article7productions_url',
            'article7exports_url', 'article7imports_url',
            'article7nonpartytrades_url', 'article7emissions_url',
            'hat_productions_url', 'hat_imports_url', 'data_others_url',
            'files', 'files_url',
            'sub_info_url', 'sub_info',
            'submission_flags_url', 'submission_remarks',
            'updated_at', 'submitted_at', 'created_by', 'last_edited_by',
            'filled_by_secretariat',
            'current_state', 'previous_state', 'available_transitions',
            'data_changes_allowed', 'is_current', 'is_cloneable',
            'changeable_flags',  'flag_provisional', 'flag_valid',
            'flag_superseded',
            'can_change_remarks_party', 'can_change_remarks_secretariat',
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

    def get_can_change_remarks_party(self, obj):
        user = self.context['request'].user
        return obj.can_change_remark(user, 'remarks_party')

    def get_can_change_remarks_secretariat(self, obj):
        user = self.context['request'].user
        return obj.can_change_remark(user, 'remarks_secretariat')


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
                'created_at', 'updated_at', 'submitted_at',
                'created_by', 'last_edited_by', 'filled_by_secretariat',
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
