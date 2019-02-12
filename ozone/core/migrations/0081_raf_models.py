# Generated by Django 2.1.4 on 2019-02-12 12:43

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import ozone.core.models.file
import ozone.core.models.reporting


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0080_questionnaire_remarks'),
    ]

    operations = [
        migrations.CreateModel(
            name='RAFImport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0)])),
                ('party', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Party')),
            ],
            options={
                'db_table': 'reporting_raf_import',
            },
        ),
        migrations.CreateModel(
            name='RAFReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remarks_party', models.CharField(blank=True, help_text='Remarks added by the reporting party', max_length=9999)),
                ('remarks_os', models.CharField(blank=True, help_text='Remarks added by the ozone secretariat', max_length=9999)),
                ('ordering_id', models.IntegerField(default=0, help_text='This allows the interface to keep the data entries in their original order, as given by the user.')),
                ('quantity_exempted', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('quantity_production', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('quantity_used', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('quantity_exported', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('quantity_destroyed', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('on_hand_start_year', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
            ],
            options={
                'db_table': 'reporting_raf',
            },
            bases=(ozone.core.models.reporting.ModifyPreventionMixin, models.Model),
        ),
        migrations.AddField(
            model_name='historicalsubmission',
            name='raf_remarks_party',
            field=models.CharField(blank=True, help_text='General RAF remarks added by the reporting party', max_length=9999),
        ),
        migrations.AddField(
            model_name='historicalsubmission',
            name='raf_remarks_secretariat',
            field=models.CharField(blank=True, help_text='General RAF remarks added by the ozone secretariat', max_length=9999),
        ),
        migrations.AddField(
            model_name='submission',
            name='raf_remarks_party',
            field=models.CharField(blank=True, help_text='General RAF remarks added by the reporting party', max_length=9999),
        ),
        migrations.AddField(
            model_name='submission',
            name='raf_remarks_secretariat',
            field=models.CharField(blank=True, help_text='General RAF remarks added by the ozone secretariat', max_length=9999),
        ),
        migrations.AddField(
            model_name='rafreport',
            name='submission',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rafreports', to='core.Submission'),
        ),
        migrations.AddField(
            model_name='rafreport',
            name='substance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Substance'),
        ),
        migrations.AddField(
            model_name='rafimport',
            name='report',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='imports', to='core.RAFReport'),
        ),
    ]