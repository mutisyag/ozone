# Generated by Django 2.1.4 on 2019-05-14 11:31

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import ozone.core.models.file


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0124_auto_20190514_1238'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProdConsMT',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('production_all_new', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('production_feedstock', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('production_essential_uses', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('production_laboratory_analytical_uses', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('production_article_5', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('production_quarantine', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('production_process_agent', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('destroyed', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('import_new', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('import_recovered', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('import_feedstock', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('import_essential_uses', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('import_laboratory_uses', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('import_quarantine', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('import_process_agent', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('export_new', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('export_recovered', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('export_feedstock', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('export_essential_uses', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('export_quarantine', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('export_process_agent', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('non_party_import', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('non_party_export', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('prod_transfer', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('calculated_production', models.FloatField(blank=True, default=None, null=True)),
                ('calculated_consumption', models.FloatField(blank=True, default=None, null=True)),
                ('party', models.ForeignKey(help_text='Party for which this aggregation was calculated', on_delete=django.db.models.deletion.PROTECT, related_name='prodconsmt_aggregations', to='core.Party')),
                ('reporting_period', models.ForeignKey(help_text='Reporting Period for which this aggregation was calculated', on_delete=django.db.models.deletion.PROTECT, related_name='prodconsmt_aggregations', to='core.ReportingPeriod')),
                ('substance', models.ForeignKey(help_text='Substance for which this aggregation was calculated', on_delete=django.db.models.deletion.PROTECT, related_name='prodconsmt_aggregations', to='core.Substance')),
            ],
            options={
                'db_table': 'aggregation_prod_cons_mt',
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='prodcons',
            name='group',
            field=models.ForeignKey(help_text='Annex Group for which this aggregation was calculated', on_delete=django.db.models.deletion.PROTECT, related_name='prodcons_aggregations', to='core.Group'),
        ),
        migrations.AlterField(
            model_name='prodcons',
            name='party',
            field=models.ForeignKey(help_text='Party for which this aggregation was calculated', on_delete=django.db.models.deletion.PROTECT, related_name='prodcons_aggregations', to='core.Party'),
        ),
        migrations.AlterField(
            model_name='prodcons',
            name='reporting_period',
            field=models.ForeignKey(help_text='Reporting Period for which this aggregation was calculated', on_delete=django.db.models.deletion.PROTECT, related_name='prodcons_aggregations', to='core.ReportingPeriod'),
        ),
        migrations.AlterUniqueTogether(
            name='prodconsmt',
            unique_together={('party', 'reporting_period', 'substance')},
        ),
    ]
