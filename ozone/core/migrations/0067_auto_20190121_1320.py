# Generated by Django 2.1.4 on 2019-01-21 10:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0066_auto_20190118_1507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article7questionnaire',
            name='has_destroyed',
            field=models.BooleanField(help_text='If set to true it allows to complete destructions data form.'),
        ),
        migrations.AlterField(
            model_name='article7questionnaire',
            name='has_emissions',
            field=models.BooleanField(help_text='If set to true it allows to complete emissions data form.'),
        ),
        migrations.AlterField(
            model_name='article7questionnaire',
            name='has_exports',
            field=models.BooleanField(help_text='If set to true it allows to complete exports data form.'),
        ),
        migrations.AlterField(
            model_name='article7questionnaire',
            name='has_imports',
            field=models.BooleanField(help_text='If set to true it allows to complete imports data form.'),
        ),
        migrations.AlterField(
            model_name='article7questionnaire',
            name='has_nonparty',
            field=models.BooleanField(help_text='If set to true it allows to complete non-party trades data form.'),
        ),
        migrations.AlterField(
            model_name='article7questionnaire',
            name='has_produced',
            field=models.BooleanField(help_text='If set to true it allows to complete productions data form.'),
        ),
        migrations.AlterField(
            model_name='article7questionnaire',
            name='remarks_os',
            field=models.CharField(blank=True, help_text='Remarks added by the ozone secretariat', max_length=9999),
        ),
        migrations.AlterField(
            model_name='article7questionnaire',
            name='remarks_party',
            field=models.CharField(blank=True, help_text='Remarks added by the reporting party', max_length=9999),
        ),
        migrations.AlterField(
            model_name='blend',
            name='blend_id',
            field=models.CharField(help_text='A unique String value identifying this blend.', max_length=64, unique=True),
        ),
        migrations.AlterField(
            model_name='blend',
            name='composition',
            field=models.CharField(blank=True, help_text='Plain-test description of the composition of the blend.', max_length=256),
        ),
        migrations.AlterField(
            model_name='blend',
            name='party',
            field=models.ForeignKey(help_text='Only custom blends will be associated with a Party.', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='custom_blends', to='core.Party'),
        ),
        migrations.AlterField(
            model_name='blend',
            name='type',
            field=models.CharField(choices=[('Zeotrope', 'ZEOTROPE'), ('Azeotrope', 'AZEOTROPE'), ('Methyl bromide', 'MeBr'), ('Other', 'OTHER'), ('Custom', 'CUSTOM')], help_text='Blend types can be Zeotrope, Azeotrope, Methyl bromide, Other or Custom.', max_length=128),
        ),
        migrations.AlterField(
            model_name='historicalsubmission',
            name='flag_has_reported_a1',
            field=models.BooleanField(default=True, help_text='If set to true it means that substances under Annex A Group 1 were reported.'),
        ),
        migrations.AlterField(
            model_name='historicalsubmission',
            name='flag_has_reported_a2',
            field=models.BooleanField(default=True, help_text='If set to true it means that substances under Annex A Group 2 were reported.'),
        ),
        migrations.AlterField(
            model_name='historicalsubmission',
            name='flag_has_reported_b1',
            field=models.BooleanField(default=True, help_text='If set to true it means that substances under Annex B Group 1 were reported.'),
        ),
        migrations.AlterField(
            model_name='historicalsubmission',
            name='flag_has_reported_b2',
            field=models.BooleanField(default=True, help_text='If set to true it means that substances under Annex B Group 2 were reported.'),
        ),
        migrations.AlterField(
            model_name='historicalsubmission',
            name='flag_has_reported_b3',
            field=models.BooleanField(default=True, help_text='If set to true it means that substances under Annex B Group 3 were reported.'),
        ),
        migrations.AlterField(
            model_name='historicalsubmission',
            name='flag_has_reported_c1',
            field=models.BooleanField(default=True, help_text='If set to true it means that substances under Annex C Group 1 were reported.'),
        ),
        migrations.AlterField(
            model_name='historicalsubmission',
            name='flag_has_reported_c2',
            field=models.BooleanField(default=True, help_text='If set to true it means that substances under Annex C Group 2 were reported.'),
        ),
        migrations.AlterField(
            model_name='historicalsubmission',
            name='flag_has_reported_c3',
            field=models.BooleanField(default=True, help_text='If set to true it means that substances under Annex C Group 3 were reported.'),
        ),
        migrations.AlterField(
            model_name='historicalsubmission',
            name='flag_has_reported_e',
            field=models.BooleanField(default=True, help_text='If set to true it means that substances under Annex E were reported.'),
        ),
        migrations.AlterField(
            model_name='historicalsubmission',
            name='flag_has_reported_f',
            field=models.BooleanField(default=False, help_text='If set to true it means that substances under Annex F were reported.'),
        ),
        migrations.AlterField(
            model_name='historicalsubmission',
            name='flag_provisional',
            field=models.BooleanField(default=False, help_text='If set to true it signals that future changes are foreseen.'),
        ),
        migrations.AlterField(
            model_name='historicalsubmission',
            name='flag_superseded',
            field=models.BooleanField(default=False, help_text='If set to true it means that the current version is not relevant anymore. When a newer version of data is Submitted, the current one is automatically flagged as Superseded.'),
        ),
        migrations.AlterField(
            model_name='historicalsubmission',
            name='flag_valid',
            field=models.NullBooleanField(default=None, help_text='If set to true it signals that the data in the current version is considered correct. Can be set by the Secretariat during Processing or at the transition between the Processing or Finalized states.'),
        ),
        migrations.AlterField(
            model_name='obligation',
            name='form_type',
            field=models.CharField(help_text='Used to generate the correct form, based on this obligation.', max_length=64),
        ),
        migrations.AlterField(
            model_name='obligation',
            name='name',
            field=models.CharField(help_text='A unique String value identifying this obligation.', max_length=256, unique=True),
        ),
        migrations.AlterField(
            model_name='reportingperiod',
            name='is_reporting_allowed',
            field=models.BooleanField(default=True, help_text='Indicates whether reporting can be performed for this reporting period. Will be False for baseline years.'),
        ),
        migrations.AlterField(
            model_name='reportingperiod',
            name='is_reporting_open',
            field=models.BooleanField(default=False, help_text='Indicates whether reporting is open/ongoing for this reporting period.'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='flag_has_reported_a1',
            field=models.BooleanField(default=True, help_text='If set to true it means that substances under Annex A Group 1 were reported.'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='flag_has_reported_a2',
            field=models.BooleanField(default=True, help_text='If set to true it means that substances under Annex A Group 2 were reported.'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='flag_has_reported_b1',
            field=models.BooleanField(default=True, help_text='If set to true it means that substances under Annex B Group 1 were reported.'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='flag_has_reported_b2',
            field=models.BooleanField(default=True, help_text='If set to true it means that substances under Annex B Group 2 were reported.'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='flag_has_reported_b3',
            field=models.BooleanField(default=True, help_text='If set to true it means that substances under Annex B Group 3 were reported.'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='flag_has_reported_c1',
            field=models.BooleanField(default=True, help_text='If set to true it means that substances under Annex C Group 1 were reported.'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='flag_has_reported_c2',
            field=models.BooleanField(default=True, help_text='If set to true it means that substances under Annex C Group 2 were reported.'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='flag_has_reported_c3',
            field=models.BooleanField(default=True, help_text='If set to true it means that substances under Annex C Group 3 were reported.'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='flag_has_reported_e',
            field=models.BooleanField(default=True, help_text='If set to true it means that substances under Annex E were reported.'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='flag_has_reported_f',
            field=models.BooleanField(default=False, help_text='If set to true it means that substances under Annex F were reported.'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='flag_provisional',
            field=models.BooleanField(default=False, help_text='If set to true it signals that future changes are foreseen.'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='flag_superseded',
            field=models.BooleanField(default=False, help_text='If set to true it means that the current version is not relevant anymore. When a newer version of data is Submitted, the current one is automatically flagged as Superseded.'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='flag_valid',
            field=models.NullBooleanField(default=None, help_text='If set to true it signals that the data in the current version is considered correct. Can be set by the Secretariat during Processing or at the transition between the Processing or Finalized states.'),
        ),
    ]
