# Overview of the *Data Submission* process

The description below covers all possible states during the submission process, together with entry conditions, possible transitions and remarks.

The ORS will be able to show at any time what the Party has submitted and what were the changes done by the Secretariat afterwards – including minor corrections.

The process of computing derived data from a submission (by the Ozone Secretariat) is outside the scope of this document and will be detailed somewhere else. This process only starts once a submission has been Finalized.

__TODO EDW - is the below section OK?__
## Common terminology
- ORS - the Ozone Reporting System
- Submission - a collection of data, possibly having several versions, for a certain Party-Reporting Period-Reporting Obligation combination. Each such combination can have one submission, but several versions.
- Version - a specific version of reported data. A version is tied to one specific submission (see below for details).

## Versioning of submissions

The ORS shall implement versioning of reported data, meaning that whenever a set of data is submitted, a copy of it is kept in the archive. We will refer to these copies as _versions_ and the term should be understood as a version of the reported data at a particular point in time.

Once a _version_ is created, __the data__ within it __never changes__. Any permanent change (done both by Party and Secretariat users) starting from the data within a _version_ will result in a __new version__.

However, a specific version's state and flags can change - and these changes will be audited/recorded by the ORS.

Each version can be viewed and manipulated independently.

Both _Party Reporter_ and _Secretariat Edit_ users can create new versions starting from existing data.

A version is always linked to a single:
- party
- reporting period
- and reporting obligation


## Access rights

In general, a submission is only visible to _reporter_ users from the corresponding Party, to the _Secretariat_ users and to the _Administrators_.
Reporters belonging to another Party are not allowed to see other's data.


## Attributes (flags) of submissions

### Provisional flag
The _provisional_ flag can be set or removed by the reporter while a Submission is _Ongoing_.
It signals that future changes (updated submissions for the same reporting period) are foreseen.
A provisional version is processed by the Ozone Secretariat like any other version. However, versions derived by the OS from provisional data will also have this flag automatically set - it can be manually unset when needed.

This flag's granularity is per version.

TODO EDW: It is likely that some additional reminders/notifications are going to be sent to the reporter at certain times during the reporting cycle (e.g. close to deadlines).
TODO Gerald: to think and agree on more details about these notifications.

### Incomplete flag
The _incomplete_ flag can be set or removed by the reporter at any time (TODO EDW - this probably requires a notification to the OS).
It signals that some data (related to some of the substance groups) is not included in the submission and that the reporter is aware of that.

The flag can be set also automatically by the ORS, but only after getting the reporter's confirmation.

This flag's granularity is per annex groups (if one substance is incomplete in a group, the whole group is incomplete).

### Invalid flag
The _invalid_ flag can be set by the Secretariat during the Processing state.
It signals that the data from the report cannot be used at all.


## Creating a version

- _Reporters_ can create a new empty version or can copy data from a previous version, as follows:

  - from _the final_ (latest _Valid_) version of any previous period - **if** no submission exists for the currently selected period. *By default*, the interface will show the most recent period which is smaller than the selected reporting period.
  - from any other intermediary submission (within the current period), but not ones for previous periods - **if** submissions for the current period already exist. *By default*, the interface will show most recent submission from current period. Copying _Valid_, _Not valid_ and _Recalled_ submissions shall be possible.

- _Secretariat_ users can create new versions on the behalf of a Party (e.g. when data is received via email).

The initial state of a new submission is _Ongoing_.

Both Party users and the Secretariat will have the ability to add supporting files to a specific version (for example emails or PDF/Excel files containing the data) - these files should only be treated as supporting info, not as actual data.

When the Secretariat picks a version from a Party to process, the source version is recorded/associated with the new version that the Secretariat creates.

If the Secretariat enters new data from a Party's email submission, the absence of a first version from the Party side will indicate that the submission was not made through the ORS.

## List of workflow states

- [Data Entry](#1-data entry)
- [Submitted](#2-submitted)
- [Recalled](#3-recalled)
- [Processing](#4-processing)
- [Finalized](#5-finalized)

## State diagram

The diagram below has been generated using https://state-machine-cat.js.org and the source code from [this file](workflow.src).

![State diagram](state_diagram.svg "State diagram")

## 1. DATA ENTRY

This represents the initial state in which data entry by a reporter has been initiated, but is still in progress and has not yet been submitted.

At any given time, there is only one _ongoing_ submission per Party and per reporting period.
However, there can be multiple _ongoing_ submissions at the same time for a given Party (for different reporting periods).

### Entry and exit

A submission can enter the _Ongoing_ state only when it is created and remains _ongoing_ until the reporter initiates the _submit_ action.

From the _Ongoing_ state, the state of the submission can change to:

- _Submitted_, at the request of the reporter (or the Secretariat acting on behalf of the reporter)

### Actions by role

#### Reporter

While a submission is ongoing, _reporter_ users (from the corresponding Party) will be able to:

- make changes to the data using the web forms
- upload data in the form of an xls or xlsx file
- delete the submission
- _submit_, which triggers the transition to _Submitted_ and sends a notification to all users holding the Secretariat role

TODO Gerald: should notifications be sent also to other (all) reporters from the same party?

TODO Gerald: should any colleague be able to submit or only the author?

#### Secretariat

_Secretariat_ users are able to view the submission details, but not make any changes.

TODO Gerald: validate that the Secretariat cannot make any changes unless they enter data on behalf of the Party (fully)
TODO Gerald: maybe a better option is to prevent changes unless the submission was created by a Secretariat user?.


## 2. SUBMITTED

In this state, data has been officially submitted by the reporter and is awaiting action from the Ozone Secretariat.

### Entry and exit

Submission which are _Ongoing_ or _Recalled_ can enter the _Submitted_ state.
From the _Submitted_ state, the state of the submission can change to:

- _Processing_: The Secretariat can change the state to Processing, so that parties know their data is being processed;
- _Valid_ or _Not valid_, at the Secretariat's request, as a shortcut (skipping the _Processing_ state);
- _Recalled_: A reporter may choose to recall a specific submission if its data is deemed incorrect, signalling to the Ozone Secretariat that the Party shall revise the data.

### Actions by role

#### Reporter

Once submitted, data cannot be edited anymore by reporters. However, a different submission may be created after _recalling_ the existing submission and optionally copying data from it.

#### Secretariat

The Secretariat can set the next state of the submission to either _Valid_ or _Not valid_, depending on their findings.

TODO EDW: link to the section where business rules and validation are described.

TODO Gerald: Anything else that the secretariat can do while a submission is Submitted?

## 3. RECALLED

This state signifies that the reporter considers this submission incorrect or incomplete. The submission is basically "frozen" (it does not return to to _Ongoing_ state and data is not physically erased, but rather archived for historical and audit purposes).

As explained above, data in a recalled submission can be copied (and then modified) to create a new submission.

### Entry and exit

Submissions which are _Submitted_ or _Processing_ can enter the _Recalled_ state.
From the _Recalled_ state, the state of the submission can change to:

- _Submitted_: A recalled submission can be _re-instated_ by the reporter, thus changing back its state back to Submitted.

TODO Gerald: When re-instating a submission, should the ORS allow changes to the data or simply it means re-submitting the same data which was recalled?

### Actions by role

#### Reporter

A reporter can re-instate the submission or create a new Ongoing submission in case changes are necessary.

#### Secretariat

Secretariat users can only view a recalled submission.

TODO Gerald: Should you be able to insert comments/remarks, etc? If so, at which stages and how granular?

## 4. PROCESSING

At this point, the Ozone Secretariat is doing the processing of the reported data and the reporter knows their data is being processed.

### Entry and exit

Only submissions which are _Submitted_ can enter the _Processing_ state.
From _Processing_, the state of the submission can change to:

- _Recalled_, at the reporter's request, or
- either one of _Valid_ or _Not valid_, based the Secretariat's decision.

### Actions by role

Reporters can _Recall_ the submission.
Secretariat users can _Validate_ or _Invalidate_ the submission.

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

### Actions by role

Reporters can only view the submission, but are allowed to create a new one in case revisioning the data is necessary.

The secretariat can invalidate a valid submission.

Since this is a final state, any further state change is not permitted.

TODO: _Recalled_?
