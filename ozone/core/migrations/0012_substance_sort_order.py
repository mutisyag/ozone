# Generated by Django 2.0.5 on 2018-11-22 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_auto_20181122_0920'),
    ]

    operations = [
        migrations.AddField(
            model_name='substance',
            name='sort_order',
            field=models.IntegerField(null=True),
        ),
    ]