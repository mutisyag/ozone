# Roles

TODO: It is foreseen that new roles will be defined in relation to the notification features.

## Administrator

Can create new users and assign permissions.

## Secretariat

Ozone Secretariat staff can:

* enter data on behalf of a Party that submits its information by means other than the online reporting tool (e.g. via e-mail)
* maintain lookup tables and other types of data; permissions granted "per-table" [^TODO1]
* act during the reporting workflow (detailed in the [workflow specifications](workflow.md))
* send notifications and reminders to Parties

[^TODO1]: More details needed, it's possible to define more specialized roles, easier to assign and manage. That will be known once the data model is finished.

## Reporter

Reporters can:
* report data for ANY reporting cycle for which they have not previously submitted data (up to the current reporting period)
* revise previous submissions (Note: revisions of data for baseline periods require a special approval)
* act during the reporting workflow (detailed in the [workflow specifications](workflow.md))

Notes:

* Each reporter is assigned to a single Party
* There can be one or more reporters for one Party.
* Differentiating among party administrators, focal points, primary contacts, secondary contacts, etc. is not necessary [^TODO2]

[^TODO2]: That can be added as a secondary (low priority) requirement (different permissions within the Party role: read-only / read-write / submit data / create additional users)

## Auditor

Auditors can **view** all data reported by any party, but can't make any changes. In general, these users belong to the Ozone Secretariat.

## Contact

Contacts belong to one party and can **view** all data reported by their party. It's similar to the _Auditor_ role, but restricted to a single Party.

## Public users

Note: Public users won't have direct access to any part of the reporting system. Some of the data is published in the main website, but from a different database.