# Generated by Django 2.1.4 on 2019-03-15 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0097_auto_20190313_1447'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article7questionnaire',
            name='remarks_os',
        ),
        migrations.RemoveField(
            model_name='article7questionnaire',
            name='remarks_party',
        ),
    ]
