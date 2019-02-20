from django.db import migrations
from django.core.serializers import base, python
from django.core.management import call_command


def refresh_obligations(apps, schema_editor):
    """
    Check 0036_obligations.py migration for a detailed explanation
    of the code below.
    """

    Submission = apps.get_model('core', 'Submission')
    Submission.objects.filter(obligation_id__gte=3).delete()
    Obligation = apps.get_model('core', 'Obligation')
    if Obligation.objects.all().count() == 0:
        return
    Obligation.objects.filter(id__gte=3).delete()

    old_get_model = python._get_model

    def _get_model(model_identifier):
        try:
            return apps.get_model(model_identifier)
        except (LookupError, TypeError):
            raise base.DeserializationError(
                "Invalid model identifier: '%s'" % model_identifier)

    python._get_model = _get_model

    try:
        call_command('loaddata', 'obligations_old_v2')
    finally:
        python._get_model = old_get_model


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0059_auto_20190114_1645'),
    ]

    operations = [
        migrations.RunPython(refresh_obligations),
    ]
