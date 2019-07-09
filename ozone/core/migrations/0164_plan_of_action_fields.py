# Generated by Django 2.1.4 on 2019-07-09 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0163_plans_of_action'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='planofaction',
            options={'ordering': ('party__name', '-reporting_period', 'group'), 'verbose_name_plural': 'plans of action'},
        ),
        migrations.AlterModelOptions(
            name='planofactiondecision',
            options={'ordering': ('-year_adopted', 'party__name')},
        ),
        migrations.AlterField(
            model_name='planofaction',
            name='annex_group_description',
            field=models.CharField(blank=True, max_length=256, verbose_name='annex group description'),
        ),
    ]