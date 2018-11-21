# Generated by Django 2.0.5 on 2018-11-20 20:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_on_delete_protect_for_submission_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blendcomponent',
            name='substance',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='blends', to='core.Substance'),
        ),
    ]
