from django.db import migrations
from django.core.management import call_command

obligation_data = [
  {
    "model": "core.obligation",
    "pk": 1,
    "fields": {
      "name": "Article 7",
      "description": "Data forms 1-6",
      "form_type": "art7",
      "has_reporting_periods": True
    }
  },
  {
    "model": "core.obligation",
    "pk": 2,
    "fields": {
      "name": "Essential and Critical uses (RAF)",
      "description": "Reporting account format",
      "form_type": "essencrit",
      "has_reporting_periods": True
    }
  },
  {
    "model": "core.obligation",
    "pk": 3,
    "fields": {
      "name": "HAT Imports and Production",
      "description": "Data forms 7 and 8",
      "form_type": "hat",
      "has_reporting_periods": True
    }
  },
  {
    "model": "core.obligation",
    "pk": 4,
    "fields": {
      "name": "Other",
      "description": "Letters and narrative reports",
      "form_type": "letter",
      "has_reporting_periods": True
    }
  }
]


def refresh_obligations(apps, schema_editor):
    Submission = apps.get_model('core', 'Submission')
    Submission.objects.filter(obligation_id__gte=3).delete()
    Obligation = apps.get_model('core', 'Obligation')
    Obligation.objects.filter(id__gte=3).delete()
    # Populate obligations
    for entry in obligation_data:
        obj = Obligation(**entry['fields'])
        obj.pk = entry['pk']
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_party_type_model'),
    ]

    operations = [
        migrations.RunPython(refresh_obligations),
    ]
