# Generated by Django 2.0.5 on 2018-09-25 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20180925_1101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='substance',
            name='rcode',
            field=models.CharField(blank=True, max_length=128, null=True, unique=True),
        ),
    ]
