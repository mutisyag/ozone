# Generated by Django 2.1.4 on 2019-07-03 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0159_auto_20190701_1238'),
    ]

    operations = [
        migrations.AddField(
            model_name='obligation',
            name='has_versions',
            field=models.BooleanField(default=True, help_text='Indicates whether submissions for this obligation can have multiple versions'),
        ),
    ]
