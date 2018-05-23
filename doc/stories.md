# Account management

## As any user, I should be able to:

- reset my password
- receive a notification when my account is created, blocked, de-activated or when my password is reset by an administrator
- authenticate using the same credentials to the ORS and to the Ozone Secretariat website

# GDPR-compliance
GDPR compliance is mandatory for European Union users but recommended for all users of the ORS.

## In compliance with GDPR, chapter 3, users should be able to:
- Give their consent before the collection of their personal data;
- Understand how their personal details are used;
- Access and update their profile;
- Download their personal details in a machine-friendly format;
- Request the erasure of their personal details


# Article 7 reporting

TODO: List of data forms

## Reporter (Party)

### 1. As a reporter, I want to be able to report ozone-related data

It should be possible to add & edit data through at least:
 - an upload interface that accepts data files conforming to the specific format defined by the Ozone Secretariat.
 - an interface that allows each relevant field to be added manually
 - an API (machine to machine) - this should allow chunks of partial data to be received, until completion
 - a combination of the above (e.g. a file can be uploaded and then manual field edits should be posssible)


Notes:
TODO

# Non-Article 7 reporting


WORK IN PROGRESS BELOW
========================


When reporting data manually through the interface, each dataform should have its own tab. The user should be able to easily switch/navigate between tabs and separately save the data entered on each of these.

Each submission will be tied to a reporting period; the Party will be able to select the period to report on in the interface, with the default being the current reporting period (*rules are in fact more complex; to be written down*).


**TODO**:

- Should the userbe able to upload exemption forms as part of a submission, so these are linked with the submitted data?
- "Annex to Data Form 6 on HFC-23 emissions"

Notes

- Reporting periods are not usually mapped to calendar years.
- There is no need to assign submissions to individual users.
- The same workflow applies to all forms (Article 7 and non-Article 7)


 
**TODO**: we could allow partial submissions (party could enter part of the data and submit it, as it becomes available).
 TODO: also consider partial submissions via the API
 
### Users should be able to view a history of their submissions.


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
 




### shall be able to view any past submission available in the system.

TODO: data migration?


### Admin: view audit (changes)
