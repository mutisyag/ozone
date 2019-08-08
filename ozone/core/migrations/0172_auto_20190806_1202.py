# Generated by Django 2.1.4 on 2019-08-06 09:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0171_auto_20190802_1130'),
    ]

    operations = [
        migrations.CreateModel(
            name='OtherCountryProfileData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=9999)),
                ('url', models.URLField(blank=True, max_length=1024, null=True, verbose_name='URL')),
                ('remarks_secretariat', models.CharField(blank=True, max_length=9999)),
                ('obligation', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='other_country_profile_data', to='core.Obligation')),
                ('party', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='other_country_profile_data', to='core.Party')),
                ('reporting_period', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='other_country_profile_data', to='core.ReportingPeriod')),
                ('submission', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='other_country_profile_data', to='core.Submission')),
            ],
            options={
                'verbose_name_plural': 'other country profile data',
                'db_table': 'other_country_profile_data',
            },
        ),
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(blank=True, max_length=1024, null=True, verbose_name='URL')),
                ('description', models.CharField(blank=True, max_length=9999)),
                ('is_url_broken', models.BooleanField(default=False)),
                ('ordering_id', models.IntegerField(default=0)),
                ('party', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='websites', to='core.Party')),
            ],
            options={
                'db_table': 'website',
            },
        ),
    ]
