# Generated by Django 2.1.4 on 2019-09-12 12:59

from django.db import migrations, models
import django.db.models.deletion
import ozone.core.models.country_profile


def dummy_upload_to(instance, filename):
    return filename


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0190_auto_20190829_1351'),
    ]

    operations = [
        migrations.CreateModel(
            name='LicensingSystemFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=dummy_upload_to)),
                ('licensing_system', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='core.LicensingSystem')),
            ],
        ),
        migrations.CreateModel(
            name='LicensingSystemURL',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(max_length=1024, verbose_name='URL')),
                ('licensing_system', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='urls', to='core.LicensingSystem')),
            ],
        ),
    ]
