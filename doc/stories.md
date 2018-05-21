# [EPIC] User roles & workflow

As a user, I should be able to perform only the actions available for my assigned user role.
Available roles:
- anonymous (can only view public data) ?
- reporter (party side)
- ozone secretariat
- admin

Focus on reporter & ozone secretariat for now.

## Reporter (Party)

### 1. As a reporter, I want to be able to report ozone-related data

It should be possible to add & edit data through at least:
 - an upload interface that accepts data files conforming to the specific format defined by the Ozone Secretariat.
 - an interface that allows each relevant field to be added manually
 - an API (machine to machine) - this should allow chunks of partial data to be received, until completion
 - a combination of the above (e.g. a file can be uploaded and then manual field edits should be posssible)

When reporting data manually through the interface, each dataform should have its own screen. The user should be able to easily switch/navigate between the data forms (and their annexes) and separately save the data entered on each of these.

Each submission will be tied to a reporting year; the Party will be able to select the year to report on in the interface, with the default being the current reporting year (*rules are in fact more complex; to be written down*).

The user should also be able to upload exemption forms as part of a submission, so these are linked with the submitted data.

**TBD**:
- concurrent editing on the same data. Assignment of report to user. De-assign upon submission.
- do we need to treat data from "Annex to Data Form 6 on HFC-23 emissions" as a completely separate report? If so, will it conform to the same data entry flow & constraints (reporting intervals, checkbox for provisional data, etc) as the Article 7 data? In short, do we need to define a different workflow for it?
- reporting cycles - will there be any specific data that needs to be entered at intervals smaller than one year (e.g. 6 months?)


### 2. Submission states
 
A submission could have the following states:
 - Data Entry in progress
 - Submitted
 - Recalled
 - Finalized (Requires Ozone Secretariat input)
 - Rejected (Requires Ozone Secretariat input)
 
Rules for data submission state changes:
 - Data can be Submitted only by its author.
 - Submitted data that fails automated checks will be returned to Data Entry state. Not all automated checks will result in this, some will only give warnings.
 - Once successfully Submitted, data cannot be edited anymore. However, a different revision may be created by copying an existing submission.
 - Once successfully Submitted, a submission can be Recalled only by its author.
 - A Recalled submission can be re-instated by its author, thus changing back its state to Submitted.
 - Once Finalized, a submission should not be editable anymore.
 - However, a Finalized submission could become Rejected at a later date (if an error in the data later becomes apparent).
 - Submitted data can be Rejected by the OS if it has problems.
 - Rejected submissions allow the creation of new revisions, which will transition it back to Data Entry in progress.
 
**TBD**: we could allow partial submissions (party could enter part of the data and submit it, as it becomes available).
 
 
### 3. As a reporter, I can create multiple revisions for each non-finalized submission

When submitting data, a new revision of the data should automatically be created and saved, with the user being notified about it.

The user should be able to view a history of his/her revisions for a submission.

It should be possible for Parties to revert to a previous revision if necessary, but user should be prompted and notified of the implications. This action should only be possible in Data Entry, Recalled or Rejected states.
 
**TBD**: is there another user need that this tries to cover, besides incrementally correcting mistakes in the reported data?
 
 
### 4. Submission flags
 
During Data Entry, several checkboxes should be available to the user.

These do not affect the transition between states, but provide a way to notify the OS that the data is provisional or incomplete:
 - Provisional data
 - Checkboxes on the completeness of the data for each annex group

*Rules for the above will be detailed when further fleshing out the story.*

 
### 5. Reporting data should be automatically checked for consistency and correctness
 
According to data reporting method, checks should be automatically triggered by:
 - uploading a new data file
 - pressing the "Submit delivery" button
 
Correctness checks should verify that all required fields have been filled.

Checks should include consistency checks, including by comparison to previous reporting years.

Automated checks should be modular, so that they can be easily modified/customized; it should also be possible to add new checks with minimal development effort.


### 6. Reporting data should be automatically checked for compliance
 
It should be possible to trigger automatic warnings when certain predefined limits are exceeded on specific fields.

These warnings could be presented to the reporting party and/or notifications should also be sent (or otherwise made visible) to the Ozone Secretariat.
 
 
### 7. The interface should display workflow progress and state to the reporter, for example in a process-like illustration.


### 8. As a Party, I want to be able to review Lookup Tables



## Ozone secretariat

### 1. As a member of the OS, I want to be able to view all submitted data


### 2. As a member of the OS, I want to be able to assign/unassign myself to/from a submission

 This avoids conflicts during submission processing or data entry.


### 3. As a member of the OS, I want to be able to enter data on behalf of a Party
 When data is received on paper, members of the OS need to be able to enter it manually.

 The state flow here should be the same as when a Party enters the data.


### 4. As a member of the OS, I want to be able to Finalize a submission
 Once Finalized, the submission is considered complete and correct.

 It is automatically de-assigned and becomes uneditable.

 If, however, at a later date it is found that the data did have problems, the submission can be transitioned to the Rejected state, which will make it possible for Parties to create a new revision.


### 5. As a member of the OS, I want to be able to Reject a submission
 



