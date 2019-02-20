from django.db import migrations
from django.core.serializers import base, python
from django.core.management import call_command


def refresh_obligations(apps, schema_editor):
    """
    loaddata command relies on django.core.serializers.python._get_model
    function to get the corresponding model from a fixture, which will
    return the most up-to-date version of a model. We need to monkey-patch it
    so it gets the historical model.
    See full explanation at https://stackoverflow.com/a/39743581
    """

    Submission = apps.get_model('core', 'Submission')
    Submission.objects.filter(obligation_id__gte=3).delete()
    Obligation = apps.get_model('core', 'Obligation')
    Obligation.objects.filter(id__gte=3).delete()

    # Save the old _get_model() function
    old_get_model = python._get_model

    # Define new _get_model() function here, which utilizes the apps argument
    # to get the historical version of a model. This piece of code is directly
    # stolen from django.core.serializers.python._get_model, unchanged.
    # However, here it has a different context, specifically, the apps variable.
    def _get_model(model_identifier):
        try:
            return apps.get_model(model_identifier)
        except (LookupError, TypeError):
            raise base.DeserializationError(
                "Invalid model identifier: '%s'" % model_identifier)

    # Replace the _get_model() function on the module, so loaddata can utilize it.
    python._get_model = _get_model

    try:
        # Call loaddata command
        call_command('loaddata', 'obligations_old_v1')
    finally:
        # Restore old _get_model() function
        python._get_model = old_get_model


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_party_type_model'),
    ]

    operations = [
        migrations.RunPython(refresh_obligations),
    ]
