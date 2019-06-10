# Generated by Django 2.1.4 on 2019-06-05 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0144_auto_20190605_1153'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalsubmission',
            name='pa_contain_technology_remarks',
            field=models.CharField(blank=True, help_text='General Process agent contain technology remarks added by the ozone secretariat', max_length=9999, verbose_name='process agent contain technology remarks'),
        ),
        migrations.AddField(
            model_name='historicalsubmission',
            name='pa_uses_reported_remarks',
            field=models.CharField(blank=True, help_text='General Process agent uses reported remarks added by the ozone secretariat', max_length=9999, verbose_name='process agent uses reported remarks'),
        ),
        migrations.AddField(
            model_name='submission',
            name='pa_contain_technology_remarks',
            field=models.CharField(blank=True, help_text='General Process agent contain technology remarks added by the ozone secretariat', max_length=9999, verbose_name='process agent contain technology remarks'),
        ),
        migrations.AddField(
            model_name='submission',
            name='pa_uses_reported_remarks',
            field=models.CharField(blank=True, help_text='General Process agent uses reported remarks added by the ozone secretariat', max_length=9999, verbose_name='process agent uses reported remarks'),
        ),
    ]