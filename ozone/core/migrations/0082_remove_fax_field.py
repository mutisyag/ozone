# Generated by Django 2.1.4 on 2019-02-12 14:41

from django.db import migrations, models
import ozone.core.models.file


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0081_raf_models'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submissioninfo',
            name='fax',
        ),
    ]
