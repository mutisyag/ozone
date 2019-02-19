# Generated by Django 2.1.4 on 2019-02-19 09:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0084_removing_postal_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubmissionFormat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
                ('description', models.CharField(blank=True, max_length=256)),
            ],
            options={
                'db_table': 'submission_format',
            },
        ),
        migrations.AddField(
            model_name='submissioninfo',
            name='submission_format',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='infos', to='core.SubmissionFormat'),
        ),
    ]
