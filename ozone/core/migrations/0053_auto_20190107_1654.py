# Generated by Django 2.1.4 on 2019-01-07 13:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0052_auto_20190107_1628'),
    ]

    operations = [
        migrations.RenameField(
            model_name='highambienttemperatureimport',
            old_name='quantity_dcpac_produced',
            new_name='quantity_dcpac',
        ),
        migrations.RenameField(
            model_name='highambienttemperatureimport',
            old_name='quantity_msac_produced',
            new_name='quantity_msac',
        ),
        migrations.RenameField(
            model_name='highambienttemperatureimport',
            old_name='quantity_sdac_produced',
            new_name='quantity_sdac',
        ),
        migrations.RenameField(
            model_name='highambienttemperatureproduction',
            old_name='quantity_dcpac_produced',
            new_name='quantity_dcpac',
        ),
        migrations.RenameField(
            model_name='highambienttemperatureproduction',
            old_name='quantity_msac_produced',
            new_name='quantity_msac',
        ),
        migrations.RenameField(
            model_name='highambienttemperatureproduction',
            old_name='quantity_sdac_produced',
            new_name='quantity_sdac',
        ),
    ]