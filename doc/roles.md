# Roles


## Administrator

Can create new users and assign permissions.

## Secretariat

Ozone Secretariat staff can:

* report on behalf of a Party
* maintain lookup tables and other types of data; permissions granted "per-table" [^TODO1]
* act during the reporting workflow
* send notifications and reminders to Parties

[^TODO1]: More details needed, it's possible to define more specialized roles, easier to assign and manage. That will be known once the data model is finished.


## Reporter

Parties can:
* report data for the current cycle
* revise previous submissions
* act during the reporting workflow

Notes:

* Each reporter is assigned to a single Party
* There can be one or more reporters for one Party.
* Differentiating among party administrators, focal points, primary contacts, secondary contacts, etc. is not necessary [^TODO2]


[^TODO2]: That can be added as a secondary (low priority) requirement (different permissions within the Party role: read-only / read-write / submit data / create additional users)


## Public users

Note: Public users won't have direct access to any part of the reporting system. Some of the data is published in the main website, but from a different database.