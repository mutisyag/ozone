# Generated by Django 2.1.4 on 2019-07-01 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0158_auto_20190701_1151'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='processagentusesreported',
            name='contain_technology',
        ),
        migrations.AddField(
            model_name='processagentusesreported',
            name='contain_technologies',
            field=models.ManyToManyField(blank=True, to='core.ProcessAgentContainTechnology'),
        ),
    ]