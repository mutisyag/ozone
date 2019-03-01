# Generated by Django 2.1.4 on 2019-03-01 12:38

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0091_auto_20190301_1323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exemptionapproved',
            name='quantity',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
        migrations.AlterField(
            model_name='nomination',
            name='quantity',
            field=models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
    ]
