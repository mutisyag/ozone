# Generated by Django 2.1.4 on 2019-01-16 13:36

from django.db import migrations, models
import ozone.core.models.file


def migrate_custom_blends(apps, schema_editor):
    Blend = apps.get_model('core', 'Blend')
    Blend.objects.exclude(party__isnull=True).update(type='Custom')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0062_auto_20190116_1601'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blend',
            name='type',
            field=models.CharField(choices=[('Zeotrope', 'ZEOTROPE'), ('Azeotrope', 'AZEOTROPE'), ('Methyl bromide', 'MeBr'), ('Other', 'OTHER'), ('Custom', 'CUSTOM')], max_length=128),
        ),
        migrations.RunPython(migrate_custom_blends)
    ]