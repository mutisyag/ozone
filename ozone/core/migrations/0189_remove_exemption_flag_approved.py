# Generated by Django 2.1.4 on 2019-08-15 16:42

from django.db import migrations, models
import ozone.core.models.file


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0188_party_isactive'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalsubmission',
            name='flag_approved',
        ),
        migrations.RemoveField(
            model_name='submission',
            name='flag_approved',
        ),
    ]