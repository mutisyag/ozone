# Generated by Django 2.1.4 on 2019-01-15 13:21

from django.db import migrations, models
import django.db.models.deletion
import ozone.core.models.file


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0060_obligations'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submissioninfo',
            name='reporting_channel',
        ),
        migrations.AddField(
            model_name='historicalsubmission',
            name='reporting_channel',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core.ReportingChannel'),
        ),
        migrations.AddField(
            model_name='submission',
            name='reporting_channel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='submission', to='core.ReportingChannel'),
        ),
    ]
