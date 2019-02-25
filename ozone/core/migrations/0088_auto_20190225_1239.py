# Generated by Django 2.1.4 on 2019-02-25 09:39

from django.db import migrations, models
from django.core.management import call_command
import django.db.models.deletion


def load_raf_type_of_uses(apps, schme_editor):
    call_command('loaddata', 'raf_type_of_uses')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0087_auto_20190220_1225'),
    ]

    operations = [
        migrations.CreateModel(
            name='RAFTypeOfUse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
                ('description', models.CharField(blank=True, max_length=256)),
            ],
            options={
                'db_table': 'raf_type_of_use',
            },
        ),
        migrations.AddField(
            model_name='rafreport',
            name='type_of_use',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='core.RAFTypeOfUse'),
        ),
        migrations.RunPython(load_raf_type_of_uses),
    ]
