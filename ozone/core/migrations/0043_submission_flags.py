# Generated by Django 2.0.5 on 2018-12-20 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_auto_20181218_1343'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalsubmission',
            name='flag_checked_blanks',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='historicalsubmission',
            name='flag_confirmed_blanks',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalsubmission',
            name='flag_has_blanks',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalsubmission',
            name='flag_has_reported_a1',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='historicalsubmission',
            name='flag_has_reported_a2',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='historicalsubmission',
            name='flag_has_reported_b1',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='historicalsubmission',
            name='flag_has_reported_b2',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='historicalsubmission',
            name='flag_has_reported_b3',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='historicalsubmission',
            name='flag_has_reported_c1',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='historicalsubmission',
            name='flag_has_reported_c2',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='historicalsubmission',
            name='flag_has_reported_c3',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='historicalsubmission',
            name='flag_has_reported_e',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='historicalsubmission',
            name='flag_has_reported_f',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='submission',
            name='flag_checked_blanks',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='submission',
            name='flag_confirmed_blanks',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='submission',
            name='flag_has_blanks',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='submission',
            name='flag_has_reported_a1',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='submission',
            name='flag_has_reported_a2',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='submission',
            name='flag_has_reported_b1',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='submission',
            name='flag_has_reported_b2',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='submission',
            name='flag_has_reported_b3',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='submission',
            name='flag_has_reported_c1',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='submission',
            name='flag_has_reported_c2',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='submission',
            name='flag_has_reported_c3',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='submission',
            name='flag_has_reported_e',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='submission',
            name='flag_has_reported_f',
            field=models.BooleanField(default=False),
        ),
    ]