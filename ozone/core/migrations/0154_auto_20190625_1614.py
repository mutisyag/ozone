# Generated by Django 2.1.4 on 2019-06-25 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0153_emails'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ProcessAgentUsesValidity',
            new_name='ProcessAgentApplicationValidity',
        ),
    ]
