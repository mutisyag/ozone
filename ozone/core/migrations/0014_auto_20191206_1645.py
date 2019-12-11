# Generated by Django 2.1.4 on 2019-12-06 13:45

from django.db import migrations


def update_group_f_name(apps, schema_editor):
    Group = apps.get_model('core', 'Group')
    Group.objects.filter(group_id='F').update(
        name='F'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_remove_reportingchannel_is_default_for_cloning'),
    ]

    operations = [
        migrations.RunPython(update_group_f_name),
    ]