# Generated by Django 2.1.4 on 2019-11-20 14:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_focal_point_address'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='licensingsystem',
            options={'ordering': ('party__name', '-date_reported_hfc', '-date_reported_ods')},
        ),
        migrations.AlterModelOptions(
            name='multilateralfund',
            options={'ordering': ('party__name',)},
        ),
        migrations.AlterModelOptions(
            name='ormreport',
            options={'ordering': ('party__name', '-reporting_period__end_date'), 'verbose_name': 'ORM report'},
        ),
        migrations.AlterModelOptions(
            name='othercountryprofiledata',
            options={'ordering': ('party__name', '-reporting_period__end_date'), 'verbose_name_plural': 'other country profile data'},
        ),
        migrations.AlterModelOptions(
            name='reclamationfacility',
            options={'ordering': ('party__name', '-date_reported'), 'verbose_name_plural': 'reclamation facilities'},
        ),
        migrations.AlterModelOptions(
            name='website',
            options={'ordering': ('party__name',)},
        ),
    ]