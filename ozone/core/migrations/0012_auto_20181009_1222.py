# Generated by Django 2.0.5 on 2018-10-09 12:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20181009_0844'),
    ]

    operations = [
        migrations.RenameField(
            model_name='highambienttemperatureimport',
            old_name='ducted_commercial_packaged_air_conditioners_production',
            new_name='quantity_ducted_commercial_packaged_air_conditioners_produced',
        ),
        migrations.RenameField(
            model_name='highambienttemperatureimport',
            old_name='multi_split_air_conditioners_production',
            new_name='quantity_multi_split_air_conditioners_produced',
        ),
        migrations.RenameField(
            model_name='highambienttemperatureimport',
            old_name='split_ducted_air_conditioners_production',
            new_name='quantity_split_ducted_air_conditioners_produced',
        ),
        migrations.RenameField(
            model_name='highambienttemperatureproduce',
            old_name='ducted_commercial_packaged_air_conditioners_production',
            new_name='quantity_ducted_commercial_packaged_air_conditioners_produced',
        ),
        migrations.RenameField(
            model_name='highambienttemperatureproduce',
            old_name='multi_split_air_conditioners_production',
            new_name='quantity_multi_split_air_conditioners_produced',
        ),
        migrations.RenameField(
            model_name='highambienttemperatureproduce',
            old_name='split_ducted_air_conditioners_production',
            new_name='quantity_split_ducted_air_conditioners_produced',
        ),
    ]
