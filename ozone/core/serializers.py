from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.authtoken.models import Token
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
    ReportingChannel,
    Language,
    Nomination,
    ExemptionApproved,
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
        data_dictionary = {}
        for entry in validated_data:
            for field in self.substance_blend_fields:
                if self.unique_with is None:
                    field_value = entry.get(field, None)
                else:
                    field_value = (entry.get(field), entry.get(self.unique_with))

                if entry.get(field, None) is None:
                    continue
                if field_value in data_dictionary:
                    raise ValidationError(_(f"Duplicate value for {field_value}"))
                data_dictionary[field_value] = entry

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

    def create(self, validated_data):
        # Call this method to check for duplicates
        self.construct_data_dictionary(validated_data)
        return super().create(validated_data)


class CurrentUserSerializer(serializers.ModelSerializer):
    """
    Used to get basic info for current user
    """
    impersonated_by = serializers.SerializerMethodField()
    language = serializers.SlugRelatedField(
        read_only=False,
        queryset=Language.objects.all(),
        many=False,
        slug_field='iso'
    )

    class Meta:
        model = User
        fields = (
            'id', 'username', 'is_secretariat', 'is_read_only', 'party',
            'first_name', 'last_name', 'email', 'language', 'role',
            'impersonated_by',
        )
        read_only_fields = (
            'id', 'username', 'is_secretariat', 'is_read_only', 'party', 'role'
        )

    def get_impersonated_by(self, obj):
        session = self.context['request'].session
        if '_impersonate' not in session:
            return None
        return User.objects.get(pk=session['_auth_user_id']).username


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
        # Enforce Custom type for new blends.
        validated_data['type'] = 'Custom'
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
    """
    Check create and update permissions on remarks for adding/updating a single
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
    """
    Check create and update permissions on remarks for adding/updating bulk
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


class Article7DestructionListSerializer(
    DataCheckRemarksBulkUpdateMixIn, BaseBulkUpdateSerializer
):
    substance_blend_fields = ['substance', 'blend']
    unique_with = None


class Article7DestructionSerializer(
    DataCheckRemarksMixIn, serializers.ModelSerializer
):
    group = serializers.CharField(
        source='substance.group.group_id', default='', read_only=True
    )

    class Meta:
        list_serializer_class = Article7DestructionListSerializer
        model = Article7Destruction
        exclude = ('submission', 'blend_item',)


class Article7ProductionListSerializer(
    DataCheckRemarksBulkUpdateMixIn, BaseBulkUpdateSerializer
):
    substance_blend_fields = ['substance', ]
    unique_with = None


class Article7ProductionSerializer(
    DataCheckRemarksMixIn, serializers.ModelSerializer
):
    group = serializers.CharField(
        source='substance.group.group_id', default='', read_only=True
    )

    class Meta:
        list_serializer_class = Article7ProductionListSerializer
        model = Article7Production
        exclude = ('submission',)


def get_field_value(initial_data_entry, field_name):
    """
    Returns the value of a numerical field from entries (dictionaries
    representing a single art7 import/export data entry) in serializer's
    self.initial_data.
    The UI can send None as a value in these fields.
    """
    ret = initial_data_entry.get(field_name, 0)
    return ret if ret is not None else 0


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
        if entry.get(party_field, None) is None:
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
                                get_field_value(entry, field) * percentage
                                for field in totals_fields
                            ]
                        )
                        sums_dictionary[substance]['quantities_sum'] += sum(
                            [
                                get_field_value(entry, field) * percentage
                                for field in quantity_fields
                            ]
                        )

            elif entry.get('substance', None):
                substance = entry.get('substance')
                sums_dictionary[substance]['totals_sum'] += sum(
                    [
                        get_field_value(entry, field) for field in totals_fields
                    ]
                )
                sums_dictionary[substance]['quantities_sum'] += sum(
                    [
                        get_field_value(entry, field)
                        for field in quantity_fields
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


class Article7ExportListSerializer(
    DataCheckRemarksBulkUpdateMixIn, BaseBulkUpdateSerializer
):
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


class Article7ExportSerializer(
    DataCheckRemarksMixIn, BaseBlendCompositionSerializer
):
    group = serializers.CharField(
        source='substance.group.group_id', default='', read_only=True
    )

    class Meta:
        list_serializer_class = Article7ExportListSerializer
        model = Article7Export
        exclude = ('submission', 'blend_item',)


class Article7ImportListSerializer(
    DataCheckRemarksBulkUpdateMixIn, BaseBulkUpdateSerializer
):
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


class Article7ImportSerializer(
    DataCheckRemarksMixIn, BaseBlendCompositionSerializer
):
    group = serializers.CharField(
        source='substance.group.group_id', default='', read_only=True
    )

    class Meta:
        list_serializer_class = Article7ImportListSerializer
        model = Article7Import
        exclude = ('submission', 'blend_item',)


class Article7NonPartyTradeListSerializer(
    DataCheckRemarksBulkUpdateMixIn, BaseBulkUpdateSerializer
):
    substance_blend_fields = ['substance', 'blend']
    unique_with = 'trade_party'


class Article7NonPartyTradeSerializer(
    DataCheckRemarksMixIn, BaseBlendCompositionSerializer
):
    group = serializers.CharField(
        source='substance.group.group_id', default='', read_only=True
    )

    class Meta:
        list_serializer_class = Article7NonPartyTradeListSerializer
        model = Article7NonPartyTrade
        exclude = ('submission', 'blend_item',)


class Article7EmissionListSerializer(
    DataCheckRemarksBulkUpdateMixIn, BaseBulkUpdateSerializer
):
    """
    The list serializer for emissions needs to delete everything
    there was and create all data fresh, as there is no field to filter on.

    This is accomplished easily by setting substance_blend_fields = []
    """
    substance_blend_fields = []


class Article7EmissionSerializer(
    DataCheckRemarksMixIn, serializers.ModelSerializer
):
    class Meta:
        list_serializer_class = Article7EmissionListSerializer
        model = Article7Emission
        exclude = ('submission',)


class HighAmbientTemperatureProductionListSerializer(
    DataCheckRemarksBulkUpdateMixIn, BaseBulkUpdateSerializer
):
    substance_blend_fields = ['substance', ]
    unique_with = None


class HighAmbientTemperatureProductionSerializer(
    DataCheckRemarksMixIn, serializers.ModelSerializer
):
    group = serializers.CharField(
        source='substance.group.group_id', default='', read_only=True
    )

    class Meta:
        list_serializer_class = HighAmbientTemperatureProductionListSerializer
        model = HighAmbientTemperatureProduction
        exclude = ('submission',)


class HighAmbientTemperatureImportListSerializer(
    DataCheckRemarksBulkUpdateMixIn, BaseBulkUpdateSerializer
):
    substance_blend_fields = ['substance', 'blend']
    unique_with = None


class HighAmbientTemperatureImportSerializer(
    DataCheckRemarksMixIn, BaseBlendCompositionSerializer
):
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


class ExemptionNominationListSerializer(
    DataCheckRemarksBulkUpdateMixIn, BaseBulkUpdateSerializer
):
    substance_blend_fields = ['substance', ]
    unique_with = None


class ExemptionNominationSerializer(
    DataCheckRemarksMixIn, serializers.ModelSerializer
):
    group = serializers.CharField(
        source='substance.group.group_id', default='', read_only=True
    )

    class Meta:
        list_serialize_class = ExemptionNominationListSerializer
        model = Nomination
        exclude = ('submission',)


class ExemptionApprovedListSerializer(
    DataCheckRemarksBulkUpdateMixIn, BaseBulkUpdateSerializer
):
    substance_blend_fields = ['substance', ]
    unique_with = None


class ExemptionApprovedSerializer(
    DataCheckRemarksMixIn, serializers.ModelSerializer
):
    group = serializers.CharField(
        source='substance.group.group_id', default='', read_only=True
    )

    class Meta:
        list_serialize_class = ExemptionApprovedListSerializer
        model = ExemptionApproved
        exclude = ('submission',)


class UpdateSubmissionInfoSerializer(serializers.ModelSerializer):
    reporting_channel = serializers.SerializerMethodField()

    class Meta:
        model = SubmissionInfo
        exclude = ('submission',)

    def get_reporting_channel(self, obj):
        return getattr(obj.submission.reporting_channel, 'name', '')

    def check_reporting_channel(self, instance, user):
        if (
            instance.submission.check_reporting_channel_modified()
            and not instance.submission.can_change_reporting_channel(user)
        ):
            raise ValidationError({
                "reporting_channel": [
                    _('User is not allowed to change the reporting channel')
                ]
            })

    def update(self, instance, validated_data):
        user = self.context['request'].user
        # Quick fix for staging error. Reporting channel info has been lost for
        # some submissions, otherwise this check wouldn't be necessary.
        if self.context.get('reporting_channel', None):
            instance.submission.reporting_channel = ReportingChannel.objects.get(
                name=self.context['reporting_channel']
            )
            self.check_reporting_channel(instance, user)
            instance.submission.save()
        return super().update(instance, validated_data)


class SubmissionInfoSerializer(serializers.ModelSerializer):
    reporting_channel = serializers.SerializerMethodField()

    class Meta:
        model = SubmissionInfo
        exclude = ('submission',)

    def get_reporting_channel(self, obj):
        return getattr(obj.submission.reporting_channel, 'name', '')


class PerTypeFieldsMixIn(object):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed/updated

    See https://www.django-rest-framework.org/api-guide/serializers/#dynamically-modifying-fields
    """

    def __init__(self, instance=None, **kwargs):
        # Instantiate the superclass normally
        super().__init__(instance=instance, **kwargs)
        try:
            # Fields and remarks return a list of
            # one.
            instance = instance[0]
        except IndexError:
            # Empty queryset.
            return
        except TypeError:
            # A detail view.
            pass
        fields = self.get_dynamic_fields(instance)
        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    @classmethod
    def get_dynamic_fields(cls, instance):
        """Get the corresponding fields"""
        if not instance:
            return
        try:
            return cls.Meta.per_type_fields[instance.obligation.form_type]
        except KeyError:
            return cls.Meta.base_fields


class SubmissionFlagsSerializer(
    PerTypeFieldsMixIn, PartialUpdateSerializerMixin, serializers.ModelSerializer,
):
    """
    Specific serializer used to present all submission flags as a nested
    object, since this is easily usable by the frontend.
    """

    class Meta:
        model = Submission
        base_fields = (
            'flag_provisional', 'flag_valid', 'flag_superseded',
        )
        per_type_fields = {
            'art7': base_fields + (
                'flag_checked_blanks', 'flag_has_blanks', 'flag_confirmed_blanks',
                'flag_has_reported_a1', 'flag_has_reported_a2',
                'flag_has_reported_b1', 'flag_has_reported_b2',
                'flag_has_reported_b3', 'flag_has_reported_c1',
                'flag_has_reported_c2', 'flag_has_reported_c3',
                'flag_has_reported_e', 'flag_has_reported_f',
            ),
            'hat': base_fields + (
                'flag_checked_blanks', 'flag_has_blanks', 'flag_confirmed_blanks',
                'flag_has_reported_a1', 'flag_has_reported_a2',
                'flag_has_reported_b1', 'flag_has_reported_b2',
                'flag_has_reported_b3', 'flag_has_reported_c1',
                'flag_has_reported_c2', 'flag_has_reported_c3',
                'flag_has_reported_e', 'flag_has_reported_f',
            ),
            'essencrit': base_fields,
            'other': base_fields,
        }
        fields = list(set(sum(per_type_fields.values(), ())))

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


class SubmissionRemarksSerializer(
    PerTypeFieldsMixIn, PartialUpdateSerializerMixin,
    serializers.ModelSerializer
):
    """
    Specific serializer used to present all submission remarks,
    since this is easily usable by the frontend.
    """

    class Meta:
        model = Submission
        base_fields = ()
        per_type_fields = {
            'art7': (
                'imports_remarks_party', 'imports_remarks_secretariat',
                'exports_remarks_party', 'exports_remarks_secretariat',
                'production_remarks_party', 'production_remarks_secretariat',
                'destruction_remarks_party', 'destruction_remarks_secretariat',
                'nonparty_remarks_party', 'nonparty_remarks_secretariat',
                'emissions_remarks_party', 'emissions_remarks_secretariat',
            ),
            'hat': (
                'hat_imports_remarks_party', 'hat_imports_remarks_secretariat',
                'hat_production_remarks_party', 'hat_production_remarks_secretariat',
            ),
            'essencrit': (),
            'other': (),
        }
        fields = list(set(sum(per_type_fields.values(), ())))

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


class SubmissionFileListSerializer(serializers.ListSerializer):
    """
    ListSerializer for SubmissionFile's
    """

    def update(self, instance, validated_data):
        """
        Implements bulk update functionality for files.
        File entries will be identified by id, not by name, to allow renames.
        """
        if not isinstance(validated_data, list):
            validated_data = [validated_data, ]

        ret = []

        for modified_entry in validated_data:
            modified_id = modified_entry.get('id', None)
            if modified_id is None:
                raise ValidationError({
                    "id": [_('File id must be specified at update')]
                })
            try:
                # `instance` is a queryset due to the `BulkCreateUpdateMixin`
                obj = instance.get(id=modified_id)
                changed = False
                # We only allow changing the name and description
                if 'name' in modified_entry:
                    obj.name = modified_entry.get('name')
                    changed = True
                if 'description' in modified_entry:
                    obj.description = modified_entry.get('description')
                    changed = True
                if changed:
                    obj.save()
                    ret.append(obj)
            except ObjectDoesNotExist:
                raise ValidationError({
                    "id": [_('Specified file id not found for this submission')]
                })

        return ret


class SubmissionFileSerializer(serializers.ModelSerializer):

    # This needs to be specified explicitly so it is allowed on updates
    id = serializers.IntegerField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = SubmissionFile
        list_serializer_class = SubmissionFileListSerializer
        exclude = ('submission', 'file',)
        read_only_fields = (
            'file_url', 'tus_id', 'upload_successful', 'created', 'updated',
            'original_name', 'suffix', 'uploader',
        )

    def get_file_url(self, obj):
        return self.context['request'].build_absolute_uri(
            reverse(
                "core:submission-files-download",
                kwargs={
                    "submission_pk": obj.submission.pk,
                    "pk": obj.pk
                }
            )
        )


class UploadTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadToken
        fields = '__all__'


class SubmissionSerializer(
    PerTypeFieldsMixIn,
    PartialUpdateSerializerMixin,
    serializers.HyperlinkedModelSerializer,

):
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

    exemption_nomination_url = serializers.HyperlinkedIdentityField(
        view_name='core:submission-exemption-nomination-list',
        lookup_url_kwarg='submission_pk',
    )
    exemption_approved_url = serializers.HyperlinkedIdentityField(
        view_name='core:submission-exemption-approved-list',
        lookup_url_kwarg='submission_pk',
    )

    # Permission-related fields
    available_transitions = serializers.SerializerMethodField()
    is_cloneable = serializers.SerializerMethodField()
    changeable_flags = serializers.SerializerMethodField()

    can_change_remarks_party = serializers.SerializerMethodField()
    can_change_remarks_secretariat = serializers.SerializerMethodField()

    can_change_reporting_channel = serializers.SerializerMethodField()

    can_upload_files = serializers.SerializerMethodField()

    can_edit_data = serializers.SerializerMethodField()

    updated_at = serializers.DateTimeField(format='%Y-%m-%d')
    created_by = serializers.StringRelatedField(read_only=True)
    last_edited_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Submission

        base_fields = (
            'id', 'party', 'reporting_period', 'obligation', 'version',
            'files', 'files_url',
            'sub_info_url', 'sub_info',
            'submission_flags_url', 'submission_remarks',
            'updated_at', 'submitted_at', 'created_by', 'last_edited_by',
            'filled_by_secretariat',
            'current_state', 'previous_state',
            'data_changes_allowed', 'is_current',
            'flag_provisional', 'flag_valid',
            'flag_superseded',

            # Permission-related fields; value is dependent on user
            'available_transitions',
            'is_cloneable',
            'changeable_flags',
            'can_change_remarks_party',
            'can_change_remarks_secretariat',
            'can_change_reporting_channel',
            'can_upload_files',
            'can_edit_data',
        )

        per_type_fields = {
            'art7': base_fields + (
                'article7questionnaire_url', 'article7questionnaire',
                'article7destructions_url', 'article7productions_url',
                'article7exports_url', 'article7imports_url',
                'article7nonpartytrades_url', 'article7emissions_url',
            ),
            'hat': base_fields + (
                'hat_productions_url', 'hat_imports_url',
            ),
            'essencrit': base_fields,
            'other': base_fields + (
                'data_others_url',
            ),
            'exemption': base_fields + (
                'exemption_nomination_url', 'exemption_approved_url',
            )
        }
        # All possible fields still need to be specified here.
        # Otherwise DRF won't load them.
        fields = list(set(sum(per_type_fields.values(), ())))

        read_only_fields = (
            'available_transitions', 'is_cloneable', 'changeable_flags',
            'can_change_remarks_party', 'can_change_remarks_secretariat',
            'can_change_reporting_channel', 'can_upload_files', 'can_edit_data'
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
        flags = set(SubmissionFlagsSerializer.get_dynamic_fields(obj))
        return flags.intersection(obj.get_changeable_flags(user))

    def get_can_change_remarks_party(self, obj):
        user = self.context['request'].user
        return obj.can_change_remark(user, 'remarks_party')

    def get_can_change_remarks_secretariat(self, obj):
        user = self.context['request'].user
        return obj.can_change_remark(user, 'remarks_secretariat')

    def get_can_change_reporting_channel(self, obj):
        user = self.context['request'].user
        return obj.can_change_reporting_channel(user)

    def get_can_upload_files(self, obj):
        user = self.context['request'].user
        return obj.can_upload_files(user)

    def get_can_edit_data(self, obj):
        user = self.context['request'].user
        return obj.can_edit_data(user)


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
    can_edit_data = serializers.SerializerMethodField()

    class Meta(CreateSubmissionSerializer.Meta):
        fields = (
            ('url',)
            + CreateSubmissionSerializer.Meta.fields
            + (
                'created_at', 'updated_at', 'submitted_at',
                'created_by', 'last_edited_by', 'filled_by_secretariat',
                'version', 'current_state', 'previous_state',
                'data_changes_allowed', 'is_current',
                'flag_provisional', 'flag_valid',
                # Permissions-related fields
                'available_transitions', 'is_cloneable', 'can_edit_data',
            )
        )
        extra_kwargs = {'url': {'view_name': 'core:submission-detail'}}

    def get_available_transitions(self, obj):
        user = self.context['request'].user
        return obj.available_transitions(user)

    def get_is_cloneable(self, obj):
        user = self.context['request'].user
        return obj.is_cloneable(user)

    def get_can_edit_data(self, obj):
        user = self.context['request'].user
        return obj.can_edit_data(user)


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
