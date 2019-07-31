# Generated by Django 2.1.4 on 2019-07-31 03:41

from django.db import migrations, models
import django.db.models.deletion
import ozone.core.models.file


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0166_party_sign_dates'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartyDeclaration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('declaration', models.TextField()),
                ('party', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='declarations', to='core.Party')),
            ],
            options={
                'db_table': 'party_declaration',
            },
        ),
    ]
