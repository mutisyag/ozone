# Overview of the *Data Submission* process

The description below covers all possible states during the submission process, together with entry conditions, possible transitions and remarks.

The ORS will be able to show at any time what the Party has submitted and what were the changes done by the Secretariat afterwards.

The process of computing derived data from a submission (by the Ozone Secretariat) is outside the scope of this document and will be detailed somewhere else. This process only starts once a submission has been Finalized.

## Common terminology
- ORS - the Ozone Reporting System
- Version - a specific version of reported data, permanently saved within the ORS, for a specific Party-Reporting Period-Reporting Obligation combination. Any such combination can have several versions, which can be created by both Secretariat and Party users.


## Versioning of submissions

The ORS shall implement versioning of reported data, meaning that whenever a set of data is submitted, a copy of it is kept in the archive. We will refer to these copies as _versions_ and the term should be understood as a version of the reported data at a particular point in time.

Once a _version_ is created, __the data__ within it is saved in the ORS and then __never changes__. Any permanent (i.e. _submitted_) change (done either by Party or Secretariat users) to the data within a _version_ will result in a __new version__, no matter how small that data change is.

However, a specific version's state and flags can change, which will __not__ trigger the creation of a new version. These changes will be audited/recorded by the ORS.

Each version can be viewed and manipulated independently.

Both _Party Reporter_ and _Secretariat Edit_ users can create new versions starting from existing data.

A version is always linked to a single:
- party
- reporting period
- and reporting obligation


## Access rights

In general, a submission is visible (read-only) to all users from its corresponding _Party_, to all _Secretariat_ users and to the _Administrators_.
Users belonging to a Party are not allowed to see other Parties' data.


## Attributes (flags) of submissions

The flags below are used to describe the completeness and correctness of a specific version and are intrinsically tied to it. Thus, changing any of these flags does not create a new version.

### Provisional flag
The _provisional_ flag can be set or removed by the reporter while a Submission is in _Data Entry_.
It signals that future changes (updated submissions for the same reporting period) are foreseen.
A version marked as _provisional_ is processed by the Ozone Secretariat like any other version. However, versions derived by the OS from provisional data will also have this flag automatically set - it can be manually unset when needed.

This flag's granularity is per version, it covers all data contained within it.

TODO EDW: It is likely that some additional reminders/notifications are going to be sent to the reporter at certain times during the reporting cycle (e.g. close to deadlines).
TODO Gerald: to think and agree on more details about these notifications.

### Incomplete flag
The _incomplete_ flag can be set or removed by the reporter at any time (TODO EDW - this probably requires a notification to the OS).
It signals that data related to some of the substance groups is not included in the submission and that the reporter is aware of that.

This flag's granularity is per annex groups (if even one substance is incomplete in a group, the whole group is incomplete).

### Invalid flag
The _invalid_ flag can be set by the Secretariat during _Processing_ or at the transition between the _Processing_ or _Finalized_ states.
It signals that the data in the current version is flawed and cannot be used at all.

### Valid flag
The _valid_ flag can be set by the Secretariat during _Processing_ or at the transition between the _Processing_ or _Finalized_ states.
It signals that the data in the current version is considered correct (with possible comments/question which might elicit the creation of a new version).

__NB__: the _Valid_ and _Invalid_ flags are mutually exclusive, they cannot be set at the same time. However, it is possible that none of them are set at a given time - which basically means that the data in a version has not been fully processed by the Secretariat yet.
Changing the state of a version from _Processing_ to _Finalized_ should only be possible when either one of these two flags is specifically set. If none are set, the ORS will ask the _Secretariat_ user for a resolution.

### Superseded flag
This automatically-computed flag marks those versions that have become superseded (i.e. are not considered current/relevant anymore). It is set by the ORS only, and its calculation is performed whenever a version enters the _Submitted_ state (either from _Data Entry_ or from user _reinstating_ a _Recalled_ one).

If a newer version of data is _Submitted_ (either by Reporter or the Secretariat), the current one (if it exists) is automatically flagged as _Superseded_ - the flag change will be performed by the ORS. The newer version becomes current.

At any point in time, at most one already-submitted version is not _superseded_ - and is considered current (per Party + Reporting Period + Obligation).

Secretariat shall be warned by the ORS when a version in _Processing_ has become _superseded_.

A version in _Data Entry_ cannot become superseded.

It is preferred for this to be a flag instead of a state, as it makes the the state transitions and their logic much easier to follow.

# TODO EDW - maybe we should have a _current_ flag instead?


## Creating a version

- _Reporters_ can create a new empty version or can copy data from a previous version, as follows:

  - from _the final_ (_Finalized_, _valid_, not _superseded_) version of any previous period - **if** no submission exists for the currently selected period. *By default*, the interface will show the most recent period which is smaller than the selected reporting period.
  - from any other intermediary submission (within the current period), but not ones for previous periods - **if** submissions for the current period already exist. *By default*, the interface will show most recent submission from current period. Copying _Finalized_ and _Recalled_ submissions shall be possible.

- _Secretariat_ users can create new versions on the behalf of a Party (e.g. when data is received via email).

The initial state of any new version is _Data Entry_.

Both Party users and the Secretariat will have the ability to add supporting files to a specific version (for example emails or PDF/Excel files containing the data) - these files should only be treated as supporting info, not as actual data.

When the Secretariat picks a version from a Party to process, the source version is recorded/associated with the new version that the Secretariat creates.

If the Secretariat enters new data from a Party's email submission, the absence of a first version from the Party side will indicate that the submission was not made through the ORS.

## List of workflow states

- [Data Entry](#1-data-entry)
- [Submitted](#2-submitted)
- [Recalled](#3-recalled)
- [Processing](#4-processing)
- [Finalized](#5-finalized)

## State diagram

The diagram below has been generated using https://state-machine-cat.js.org and the source code from [this file](workflow.src).

![State diagram](state_diagram.svg "State diagram")

## 1. DATA ENTRY

This represents the initial state in which data entry by a reporter has been initiated, but is still in progress and has not yet been submitted.

At any given time, there is at most one _Data Entry_ submission per Party + obligation + reporting period.
However, there can be multiple _data entry_ submissions at the same time for a given Party (for different reporting periods).

### Entry and exit

A submission can enter the _Data Entry_ state only when it is created and remains in it until the reporter initiates the _submit_ action.

From the _Data Entry_ state, the state of the submission can change to:

- _Submitted_, at the request of the reporter 
- _Finalized_ (with _valid_ flag set), if the version has been submitted by the Secretariat acting upon written request of the Party. In this case, as the OS made the version, the state is fast-tracked to _Finalized_ as no processing is needed.


### Actions by role

#### Reporter

While a submission is in _Data Entry_, _Party Reporter_ users (from the corresponding Party) will be able to:

- make changes to the data using the web forms
- upload data in the form of an xls or xlsx file, that can be automatically converted to ORS data
- upload supporting files (PDF, Excel, emails) that will be attached to this specific version
- delete the submission
- _Submit_, which triggers the transition to _Submitted_ and sends a notification to all users holding the Secretariat role _and_ all reporters from the corresponding Party.
__NB:__ Any _Party Reporter_ user from the corresponding Party should be able to press the _Submit_ button.

#### Secretariat

In case the version was initiated by a _Party Reporter_ user:
- _Secretariat_ users are able to view the submission details, but not make any changes.

In case the version was initiated by a _Secretariat Edit_ user:
- all permissions listed above for _Reporters_ (make changes, upload, delete, submit etc) apply to _Secretariat_ users too, as this is data entered upon written request of the Party.


## 2. SUBMITTED

In this state, data has been officially submitted by the reporter and is awaiting action from the Ozone Secretariat.

### Entry and exit

Versions which are in  _Data Entry_ or _Recalled_ can enter the _Submitted_ state.
From the _Submitted_ state, the state of the version can change to:

- _Processing_: The Secretariat can change the state to Processing, so that parties know their data is being processed;
- _Recalled_: A reporter may choose to recall a specific version if its data is deemed incorrect, signalling to the Ozone Secretariat that the Party shall revise the data.

### Actions by role

#### Reporter

Once submitted, data cannot be edited anymore by reporters, they can just view it.
However, a new version may be created, optionally copying data from the current one.

#### Secretariat

The Secretariat can set the next state of the version to _Processing_.

TODO EDW: link to the section where business rules and validation are described.

TODO Gerald: Anything else that the secretariat can do while a submission is Submitted?


## 3. RECALLED

This state signifies that the reporter considers this version incorrect or incomplete. The version is basically "frozen" and moved aside. (it does not return to to _Data Entry_ state and data is not physically erased - all information needed to re-instate the version at a later date is kept, including its original state).

As explained above, data in a recalled version can be copied (and then modified) to create a new version.

When a version is _Recalled_, the Secretariat should be notified. If there is a _Data Entry_ version (created by the Secretariat) based on the Party version that is now _Recalled_, OS should be notified that they are modifying possibly obsolete data.

_Recalling_ a version also means that the "current" version has to change. If there are any versions flagged as _Superseded_, the most recent one will be un-flagged and will become the current version. If there are no _Superseded_ versions to make current, there will be no current version.

### Entry and exit

Submissions which are _Submitted_, _Processing_ or _Finalized_ can enter the _Recalled_ state, as long as they are not considered _superseded_, in which case the transition would be pointless.

From the _Recalled_ state, the state of the version can change to:

- the state it had prior to being _Recalled_ (one of _Submitted_, _Processing_ or _Finalized_): A recalled version can be _re-instated_ by the reporter, thus changing its state back to what it was before. In this case, any other version becomes _superseded_ and the re-instated one becomes "current".

### Actions by role

#### Reporter

A reporter can re-instate the version or create a new version (in _Data Entry_) in case changes are necessary.

#### Secretariat

Secretariat users can only view a recalled version.

TODO Gerald: Should you be able to insert comments/remarks, etc? If so, at which stages and how granular?


## 4. PROCESSING

At this point, the Ozone Secretariat is doing the processing of the reported data and the reporter knows their data is being processed.

If the _Secretariat_ wishes at this point to change the data, they will create a __new version__, in _Data Entry_ state, based on the version being _Processed_. The ORS will keep track of the link between this new version and the initial _processed_ version and notify the Secretariat if that becomes _Recalled_.

### Entry and exit

Only versions which are _Submitted_ and current (not _superseded_) can enter the _Processing_ state.
From _Processing_, the state of the version can change to:

- _Recalled_, at the reporter's request, or
- _Finalized_, with either one of _valid_ or _not valid_ flags set, based the Secretariat's decision.

### Actions by role

Reporters can view the version or _Recall_ it.
Secretariat users can _Finalize_ the version.

TODO EDW: link to the section where business rules are described.


## 5. FINALIZED

At this point, the Ozone Secretariat considers that the data has been fully processed and is either valid or invalid.

The Ozone Secreatariat considers such a version either:
- correct (with possible assumptions and comments - in which case it is up to the *Party* to create a new version based on this data, if any of the OS's comments require action)
- incorrect - in which case it is up to the *Party* to supply a new version

The Ozone Secretariat will be allowed to reconsider their initial decision and change the _Valid_ flag to _Not valid_ when necessary (e.g. in case of a mistake) and viceversa.

TODO Gerald: More details about *commenting* (adding remarks or further instructions) feature.


### Entry and exit

Submission found in _Submitted_ and  _Processing_ states can enter the _Finalized_ state.

From _Finalized_, the state of the version can only change to _Recalled_, through specific action of the _Party_. Any other state change is not permitted.

### Actions by role

Reporters can view the version or _Recall_ it. They may create a new one in case changes to the data are necessary.

The secretariat can invalidate a valid version and vice-versa.

