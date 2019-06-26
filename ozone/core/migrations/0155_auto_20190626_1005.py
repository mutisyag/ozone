# Generated by Django 2.1.4 on 2019-06-26 07:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0154_auto_20190625_1614'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='processagentusesreported',
            name='process_number',
        ),
        migrations.RemoveField(
            model_name='processagentusesreported',
            name='validity',
        ),
        migrations.AddField(
            model_name='processagentusesreported',
            name='application',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='pa_uses_reported', to='core.ProcessAgentApplication'),
        ),
        migrations.AddField(
            model_name='processagentusesreported',
            name='decision',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='pa_uses_reported', to='core.Decision'),
        ),
    ]
