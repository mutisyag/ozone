# Generated by Django 2.1.4 on 2019-06-14 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0151_gwp_baseline'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blend',
            options={'ordering': ['sort_order', 'pk']},
        ),
        migrations.AlterModelOptions(
            name='blendcomponent',
            options={'ordering': ['blend__sort_order', 'substance__sort_order']},
        ),
        migrations.AlterModelOptions(
            name='substance',
            options={'ordering': ['sort_order', 'pk']},
        ),
    ]