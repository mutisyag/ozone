# Generated by Django 2.1.4 on 2019-04-08 13:48

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0109_auto_20190401_1515'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProdCons',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('production_all_new', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('production_feedstock', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('production_essential_uses', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('production_laboratory_analytical_uses', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('production_article_5', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('production_quarantine', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('production_process_agent', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('consumption_lab_uses', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
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
                ('essential_uses_production', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('essential_uses_import', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('bdn_prod_limit', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('prod_transfer', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('essen_crit_exempted_amount', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('limit_prod', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('limit_cons', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('calculated_production', models.FloatField(blank=True, default=None, null=True)),
                ('calculated_consumption', models.FloatField(blank=True, default=None, null=True)),
                ('group', models.ForeignKey(help_text='Annex Group for which this aggregation was calculated', on_delete=django.db.models.deletion.PROTECT, related_name='prod_cons_aggregations', to='core.Group')),
                ('party', models.ForeignKey(help_text='Party for which this aggregation was calculated', on_delete=django.db.models.deletion.PROTECT, related_name='prod_cons_aggregations', to='core.Party')),
                ('reporting_period', models.ForeignKey(help_text='Reporting Period for which this aggregation was calculated', on_delete=django.db.models.deletion.PROTECT, related_name='prod_cons_aggregations', to='core.ReportingPeriod')),
            ],
            options={
                'db_table': 'aggregation_prod_cons',
            },
        ),
        migrations.AlterField(
            model_name='baseline',
            name='baseline_type',
            field=models.ForeignKey(help_text='Baseline type: A5/NA5 Prod/Cons or BDN', on_delete=django.db.models.deletion.PROTECT, related_name='baselines', to='core.BaselineType'),
        ),
        migrations.AlterField(
            model_name='controlmeasure',
            name='baseline_type',
            field=models.ForeignKey(help_text='Baseline type: A5/NA5 Prod/Cons or BDN', on_delete=django.db.models.deletion.PROTECT, related_name='control_measures', to='core.BaselineType'),
        ),
        migrations.AlterField(
            model_name='limit',
            name='limit_type',
            field=models.CharField(choices=[('Production', 'PRODUCTION'), ('Consumption', 'CONSUMPTION'), ('BDN', 'BDN')], help_text='Limit types can be Production, Consumption and BDN', max_length=64),
        ),
        migrations.AlterUniqueTogether(
            name='prodcons',
            unique_together={('party', 'reporting_period', 'group')},
        ),
    ]
