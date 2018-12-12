from django.db import migrations
from django.core.management import call_command


def refresh_obligations(apps, schema_editor):
    Submission = apps.get_model('core', 'Submission')
    Submission.objects.filter(obligation_id__gte=3).delete()
    Obligation = apps.get_model('core', 'Obligation')
    Obligation.objects.filter(id__gte=3).delete()
    call_command('loaddata', 'obligations')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_party_type_model'),
    ]

    operations = [
        migrations.RunPython(refresh_obligations),
    ]
