import enum

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .meeting import Treaty


__all__ = [
    'Annex',
    'Group',
    'Substance',
    'Blend',
    'BlendComponent',
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

    description = models.CharField(max_length=256)

    control_treaty = models.ForeignKey(
        Treaty, related_name='control_substance_groups', on_delete=models.PROTECT
    )
    report_treaty = models.ForeignKey(
        Treaty, related_name='report_substance_groups', on_delete=models.PROTECT
    )

    phase_out_year_article_5 = models.DateField(blank=True, null=True)
    phase_out_year_non_article_5 = models.DateField(blank=True, null=True)

    # TODO: should this be a foreign key?
    exemption = models.CharField(max_length=64, blank=True)

    # TODO: figure out a way to model consumption and production baselines.
    # These will probably have to sit in a special table, with foreign keys
    # to parties and Group IDs

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

    # In the existing data tables there is a special case:
    # the 'Other Substances' dummy substance, for which these can be null.
    # That should be modeled differently, by a nullable foreign key to
    # `Substance`, instead of making a lot of fields nullable in this model.
    annex = models.ForeignKey(
        Annex, related_name='substances', on_delete=models.PROTECT
    )
    group = models.ForeignKey(
        Group, related_name='substances', on_delete=models.PROTECT
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

    # Existing data seems to suggest this field is always non-blank,
    # allowing it though just in case...
    carbons = models.CharField(max_length=128, blank=True)

    hydrogens = models.CharField(max_length=128, blank=True)

    fluorines = models.CharField(max_length=128, blank=True)

    chlorines = models.CharField(max_length=128, blank=True)

    bromines = models.CharField(max_length=128, blank=True)

    # Remarks
    remark = models.CharField(max_length=256, blank=True)

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

    blend_id = models.CharField(max_length=64, unique=True)

    # This is a plain-text description of the composition; see `BlendComponent`
    # model for a relational one
    composition = models.CharField(max_length=256)

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

    def __str__(self):
        return self.blend_id


class BlendComponent(models.Model):
    """
    Model describing the substances composition of each blend
    """
    blend = models.ForeignKey(
        Blend, related_name='components', on_delete=models.PROTECT
    )

    # TODO: 'Ozone Business Data Tables' document *seems* to suggest that
    # the SubstanceRCode should be used instead - any need for that?
    substance = models.ForeignKey(
        Substance, related_name='blends', on_delete=models.PROTECT
    )

    percentage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )

    def __str__(self):
        return f'Blend {self.blend.blend_id} - substance {self.substance.name}'

    class Meta:
        ordering = ('blend', 'substance')
