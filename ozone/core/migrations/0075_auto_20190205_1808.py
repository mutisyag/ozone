# Generated by Django 2.1.4 on 2019-02-05 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0074_auto_20190201_1847'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exemptionapproved',
            name='emergency',
        ),
        migrations.AddField(
            model_name='historicalsubmission',
            name='flag_approved',
            field=models.NullBooleanField(default=None, help_text='If set to true it means that the nomination was approved.'),
        ),
        migrations.AddField(
            model_name='historicalsubmission',
            name='flag_emergency',
            field=models.BooleanField(default=False, help_text='If set to true it means that ozone secretariat can fill out only the Approved form directly.'),
        ),
        migrations.AddField(
            model_name='submission',
            name='flag_approved',
            field=models.NullBooleanField(default=None, help_text='If set to true it means that the nomination was approved.'),
        ),
        migrations.AddField(
            model_name='submission',
            name='flag_emergency',
            field=models.BooleanField(default=False, help_text='If set to true it means that ozone secretariat can fill out only the Approved form directly.'),
        ),
        migrations.AlterField(
            model_name='historicalsubmission',
            name='_workflow_class',
            field=models.CharField(choices=[('empty', 'Empty'), ('base', 'Base'), ('default', 'Default'), ('accelerated', 'Accelerated'), ('default_exemption', 'Default_exemption'), ('accelerated_exemption', 'Accelerated_exemption')], db_column='workflow_class', default='empty', max_length=32),
        ),
        migrations.AlterField(
            model_name='submission',
            name='_workflow_class',
            field=models.CharField(choices=[('empty', 'Empty'), ('base', 'Base'), ('default', 'Default'), ('accelerated', 'Accelerated'), ('default_exemption', 'Default_exemption'), ('accelerated_exemption', 'Accelerated_exemption')], db_column='workflow_class', default='empty', max_length=32),
        ),
    ]
