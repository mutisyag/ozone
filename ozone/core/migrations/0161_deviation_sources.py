# Generated by Django 2.1.4 on 2019-07-04 13:53

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0160_obligation_has_versions'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeviationSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('production', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('consumption', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('remark', models.CharField(blank=True, max_length=512)),
            ],
            options={
                'db_table': 'deviation_source',
            },
        ),
        migrations.CreateModel(
            name='DeviationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deviation_type_id', models.CharField(max_length=256, unique=True)),
                ('description', models.CharField(blank=True, max_length=256)),
                ('deviation_pc', models.CharField(choices=[('A', 'A'), ('P', 'P'), ('C', 'C')], max_length=16)),
                ('remark', models.CharField(blank=True, max_length=512)),
            ],
            options={
                'db_table': 'deviation_type',
            },
        ),
        migrations.AddField(
            model_name='deviationsource',
            name='deviation_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='deviation_sources', to='core.DeviationType'),
        ),
        migrations.AddField(
            model_name='deviationsource',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='deviation_sources', to='core.Group'),
        ),
        migrations.AddField(
            model_name='deviationsource',
            name='party',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='deviation_sources', to='core.Party'),
        ),
        migrations.AddField(
            model_name='deviationsource',
            name='reporting_period',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='deviation_sources', to='core.ReportingPeriod'),
        ),
        migrations.AlterUniqueTogether(
            name='deviationsource',
            unique_together={('party', 'reporting_period', 'group', 'deviation_type')},
        ),
    ]