import enum

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .meeting import ExemptionTypes, Treaty
from .party import Party

__all__ = [
    'Annex',
    'Group',
    'UsesType',
    'Substance',
    'Blend',
    'BlendComponent',
    'ProcessAgentApplication',
]


class Annex(models.Model):
    """
    Substance Annex information
    """
    annex_id = models.CharField(max_length=16, unique=True)

    name = models.CharField(max_length=64, unique=True)

    description = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'annexes'
        ordering = ('name',)


class Group(models.Model):
    """
    Substance Group information
    """
    group_id = models.CharField(max_length=16, unique=True)

    annex = models.ForeignKey(
        Annex, related_name='groups', on_delete=models.PROTECT
    )

    name = models.CharField(max_length=64, unique=True, default="")

    description = models.CharField(max_length=256)

    control_treaty = models.ForeignKey(
        Treaty,
        related_name='control_substance_groups',
        on_delete=models.PROTECT
    )
    report_treaty = models.ForeignKey(
        Treaty,
        related_name='report_substance_groups',
        on_delete=models.PROTECT
    )

    phase_out_year_article_5 = models.DateField(blank=True, null=True)
    phase_out_year_non_article_5 = models.DateField(blank=True, null=True)

    # TODO: should this be a foreign key?
    exemption = models.CharField(
        max_length=64,
        choices=((e.value, e.name) for e in ExemptionTypes),
        blank=True
    )

    def __str__(self):
        return f'Group {self.group_id}'

    class Meta:
        ordering = ('annex', 'group_id')


class Substance(models.Model):
    """
    Stores all info for a specific substance
    """

    substance_id = models.IntegerField(unique=True)

    name = models.CharField(max_length=64, unique=True)
    description = models.CharField(max_length=256)

    # Having a null group means that the substance is not controlled.
    # The annex information is present in the group (`Substance.group.annex`).
    group = models.ForeignKey(
        Group,
        null=True,
        blank=True,
        related_name='substances',
        on_delete=models.PROTECT
    )

    # Ozone-depleting potential
    odp = models.FloatField()
    # TODO: any info on when the below two are used?
    min_odp = models.FloatField()
    max_odp = models.FloatField()

    # Global warming potential
    gwp = models.IntegerField(null=True)

    formula = models.CharField(max_length=256)

    number_of_isomers = models.SmallIntegerField(null=True)

    # TODO: what is this?
    gwp2 = models.IntegerField(null=True)
    gwp_error_plus_minus = models.IntegerField(null=True)

    # Existing data seems to suggest this field is always non-blank,
    # allowing it though just in case...
    carbons = models.CharField(max_length=128, blank=True)

    hydrogens = models.CharField(max_length=128, blank=True)

    fluorines = models.CharField(max_length=128, blank=True)

    chlorines = models.CharField(max_length=128, blank=True)

    bromines = models.CharField(max_length=128, blank=True)

    # Remarks
    remark = models.CharField(max_length=256, blank=True)

    r_code = models.CharField(
        max_length=128, unique=True, blank=True, null=True
    )

    mp_control = models.CharField(max_length=256, blank=True)

    main_usage = models.CharField(max_length=256, blank=True)

    sort_order = models.IntegerField(null=True)

    @property
    def is_qps(self):
        """
        Indicates whether this substance can be used for QPS
        """
        if self.group:
            return self.group.annex.annex_id == 'E'
        return False

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('group', 'substance_id')


class Blend(models.Model):
    """
    Description of blends
    """

    @enum.unique
    class BlendTypes(enum.Enum):
        ZEOTROPE = 'Zeotrope'
        AZEOTROPE = 'Azeotrope'
        MeBr = 'Methyl bromide'
        OTHER = 'Other'

    blend_id = models.CharField(max_length=64, unique=True)

    # Custom blends will always be associated with (and only available for)
    # the Party by which they have been created (in case they've been created
    # by Secretariat using the reporting interface, they will be associated
    # with the Party to which the Submission belongs).
    party = models.ForeignKey(
        Party,
        related_name='custom_blends',
        null=True,
        on_delete=models.PROTECT
    )

    # This is a plain-text description of the composition; see `BlendComponent`
    # model for a relational one
    composition = models.CharField(max_length=256, blank=True)

    other_names = models.CharField(max_length=256, blank=True)

    type = models.CharField(
        max_length=128, choices=((s.value, s.name) for s in BlendTypes)
    )

    odp = models.FloatField(null=True)

    gwp = models.IntegerField(null=True)

    hfc = models.NullBooleanField()

    hcfc = models.NullBooleanField()

    mp_control = models.CharField(max_length=256, blank=True)

    main_usage = models.CharField(max_length=256, blank=True)

    remark = models.CharField(max_length=256, blank=True)

    sort_order = models.IntegerField(null=True, default=0)

    @property
    def custom(self):
        return self.party is not None

    @property
    def is_qps(self):
        return any(
            [
                c.substance.is_qps
                for c in self.components.all() if c.substance
            ]
        )

    def __str__(self):
        return self.blend_id


class BlendComponent(models.Model):
    """
    Model describing the substances composition of each blend
    """

    blend = models.ForeignKey(
        Blend, related_name='components', on_delete=models.PROTECT
    )

    substance = models.ForeignKey(
        Substance,
        null=True,
        blank=True,
        related_name='blends',
        on_delete=models.PROTECT
    )

    percentage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )

    component_name = models.CharField(max_length=256, blank=True)

    cnumber = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return f'Blend {self.blend.blend_id} - component {self.component_name}'

    def clean(self):
        if not self.component_name and not self.substance:
            raise ValidationError(
                {
                    'component_name': [_(
                        "Substance or component name must be set."
                    )],
                    'substance': [_(
                        "Substance or component name must be set."
                    )]
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.component_name:
            # If a component name is not given, set it to substance.name.
            # This avoids creating a property returning one of the two, which
            # would cause problems with DRF's serializers
            self.component_name = self.substance.name
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ('blend', 'substance')


class ProcessAgentApplication(models.Model):
    """
    Applications of controlled substances as process agents, as approved
    in table A of decision X/14 and updated periodically by the Meeting of the
    Parties.
    """

    decision = models.CharField(max_length=256, blank=True)

    counter = models.PositiveIntegerField()

    substance = models.ForeignKey(Substance, on_delete=models.PROTECT)

    application = models.CharField(max_length=256)

    remark = models.CharField(max_length=512, blank=True)


class UsesType(models.Model):
    """
    The different categories of uses of controlled substances that need to be
    reported.
    """

    uses_type_id = models.CharField(max_length=16, unique=True)

    name = models.CharField(max_length=128, unique=True)

    remark = models.CharField(max_length=256, blank=True)

    decision_flag = models.BooleanField()

    forms = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
