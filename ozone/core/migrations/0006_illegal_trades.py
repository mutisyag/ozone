# Generated by Django 2.1.4 on 2019-10-25 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20191021_1348'),
    ]

    operations = [
        migrations.AddField(
            model_name='illegaltrade',
            name='reported_by',
            field=models.CharField(blank=True, max_length=9999),
        ),
        migrations.AddField(
            model_name='illegaltrade',
            name='submission_year',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]
