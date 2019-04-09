# Generated by Django 2.1.4 on 2019-03-26 13:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0102_defaults_for_submission_format'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='language',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.PROTECT, related_name='users', to='core.Language'),
        ),
    ]