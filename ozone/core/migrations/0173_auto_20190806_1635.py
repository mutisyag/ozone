# Generated by Django 2.1.4 on 2019-08-06 13:35

from django.db import migrations, models
import django.db.models.deletion
import ozone.core.models.country_profile


def dummy_upload_to(instance, filename):
    return filename


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0172_auto_20190806_1202'),
    ]

    operations = [
        migrations.AddField(
            model_name='othercountryprofiledata',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=dummy_upload_to),
        ),
        migrations.AddField(
            model_name='website',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=dummy_upload_to),
        ),
        migrations.AlterField(
            model_name='focalpoint',
            name='submission',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='focal_points', to='core.Submission'),
        ),
        migrations.AlterField(
            model_name='licensingsystem',
            name='submission',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='licensing_systems', to='core.Submission'),
        ),
        migrations.AlterField(
            model_name='othercountryprofiledata',
            name='submission',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='other_country_profile_data', to='core.Submission'),
        ),
    ]
