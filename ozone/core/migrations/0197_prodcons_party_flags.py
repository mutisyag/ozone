# Generated by Django 2.1.4 on 2019-09-20 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0196_substances_formula_optional'),
    ]

    operations = [
        migrations.AddField(
            model_name='prodcons',
            name='is_article5',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='prodcons',
            name='is_eu_member',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='prodconsmt',
            name='is_article5',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='prodconsmt',
            name='is_eu_member',
            field=models.NullBooleanField(),
        ),
    ]