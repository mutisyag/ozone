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
      "name": "Transfer or addition of production or consumption",
      "description": "",
      "form_type": "other",
      "has_reporting_periods": True,
      "other": True
    }
  },
  {
    "model": "core.obligation",
    "pk": 5,
    "fields": {
      "name": "Laboratory and analytical uses",
      "description": "",
      "form_type": "other",
      "has_reporting_periods": True,
      "other": True
    }
  },
  {
    "model": "core.obligation",
    "pk": 6,
    "fields": {
      "name": "Process agent uses",
      "description": "",
      "form_type": "other",
      "has_reporting_periods": True,
      "other": True
    }
  },
  {
    "model": "core.obligation",
    "pk": 7,
    "fields": {
      "name": "Licensing information",
      "description": "",
      "form_type": "other",
      "has_reporting_periods": True,
      "other": True
    }
  },
  {
    "model": "core.obligation",
    "pk": 8,
    "fields": {
      "name": "Research, development, public awareness and exchange of information",
      "description": "",
      "form_type": "other",
      "has_reporting_periods": True,
      "other": True
    }
  },
  {
    "model": "core.obligation",
    "pk": 9,
    "fields": {
      "name": "Requests for changes in reported baseline data",
      "description": "",
      "form_type": "other",
      "has_reporting_periods": True,
      "other": True
    }
  },
  {
    "model": "core.obligation",
    "pk": 10,
    "fields": {
      "name": "Other information",
      "description": "",
      "form_type": "other",
      "has_reporting_periods": True,
      "other": True
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
        ('core', '0059_auto_20190114_1645'),
    ]

    operations = [
        migrations.RunPython(refresh_obligations),
    ]
