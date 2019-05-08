# Generated by Django 2.1.4 on 2019-04-23 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0117_nullable_baselines_limits'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article7export',
            name='decision_critical_uses',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='article7export',
            name='decision_essential_uses',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='article7export',
            name='decision_high_ambient_temperature',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='article7export',
            name='decision_laboratory_analytical_uses',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='article7export',
            name='decision_other_uses',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='article7export',
            name='decision_process_agent_uses',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='article7export',
            name='decision_quarantine_pre_shipment',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='article7import',
            name='decision_critical_uses',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='article7import',
            name='decision_essential_uses',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='article7import',
            name='decision_high_ambient_temperature',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='article7import',
            name='decision_laboratory_analytical_uses',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='article7import',
            name='decision_other_uses',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='article7import',
            name='decision_process_agent_uses',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='article7import',
            name='decision_quarantine_pre_shipment',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='article7production',
            name='decision_critical_uses',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='article7production',
            name='decision_essential_uses',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='article7production',
            name='decision_high_ambient_temperature',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='article7production',
            name='decision_laboratory_analytical_uses',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='article7production',
            name='decision_other_uses',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='article7production',
            name='decision_process_agent_uses',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='article7production',
            name='decision_quarantine_pre_shipment',
            field=models.CharField(blank=True, max_length=512),
        ),
    ]