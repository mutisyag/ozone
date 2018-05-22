Here is a complete overview of the process of *Data Submission* for a *Party*.

We are going to discuss each possible state during the submission process, together with the possible transitions:

##1. Ongoing (data entry in progress)

This is the initial state in which data entry is in progress, but the current version of the data has not been submitted yet.

There shall be at most one **Ongoing** (data entry in progress/submission of data) submission for a *Party*, for the same reporting year, at any given time. However, data for several different years could be in the **Ongoing** state at the same time.

At this stage, it should be possible for *Parties* to copy a previous submission in order to create a new one, as follows:
- when creating the first submission for a certain year, allow them to copy data from *the final* submission of any previous year. *By default:* the most recent year which is smaller than the selected reporting year.
- otherwise, allow them to pick any other intermediary submission (within the current year), but not ones for previous years. *By default:* most recent submission from current year. Copying Recalled submission shall be possible.

####Possible transitions from this state:
- to **Submitted**: from Ongoing, data can become Submitted by the *Party* once the Submit button is pressed. In this case, a new *Submission* (which can be thought of as a version/revision of data for the current year) is created. 

**N.B.:** The data for a given year can have multiple *Submissions* (versions):
- The first *Submission* (version) for a given year is only created after the Submit button is pushed for the first time.
- Each new Submit action for the same year will generate a new *Submission* (version of the data) that can be viewed and manipulated independently.


##2. Submitted

In this state, data has been officially submitted by the *Party* and is awaiting action from the *Ozone Secretariat*.

Data can be only submitted by its author (either the *Party* or, in the case of data received via mail, the *Ozone Secretariat* on behalf of the Party).

Once successfully Submitted, data cannot be edited anymore. However, a different revision may be created by copying an existing submission.

####Possible transitions from this state:
- to **Processing**: The *Ozone Secretariat* can change the state to **Processing**, so that parties know their data is being processed.
- to **Recalled**: A *Party* may choose to recall a specific *Submission* if its data is deemed incorrect, signalling to the *Ozone Secretariat* that the *Party* needs to revise its data.


##3. Recalled

This state signifies that the *Party* considers this *Submission* incorrect. The data is basically "frozen", **does not** return to **Ongoing**.

The data can be recalled only by the *Party* that submitted it.

The data in this *Submission* can be copied (and then modified) to create a new *Submission*.

####Possible transitions from this state:
- to **Submitted**: A **Recalled** submission can be re-instated only by its *Party*, thus changing back its state to **Submitted**.


##4. Processing
*Entering this state requires Ozone Secretariat input.*

The *Ozone Secretariat* can change a **Submitted** submission to **Processing**, so that the party knows their data is being processed.

At this point, the *Ozone Secretariat* is doing the handling of the data.

####Possible transitions from this state:
- to **Recalled**: A *Party* can recall a *Submission* that is being **Processed** if it realizes there is an error.
- to **Valid**: If the *Ozone Secretariat* considers the data correct, it will change it to **Valid**. 
- to **Invalid**: Submitted data can be rejected by the *Ozone Secretariat* if it has problems. To correct the errors, the *Party* is required to create a new *Submission*, which can be based on the rejected data (with the necessary modifications).



##5. Valid
*Entering this state requires Ozone Secretariat input.*

Such a *Submission* is considered correct by the *Ozone Secretariat* - with possible assumptions and comments. It is up to the *Party* to copy the data, make changes and create a new Submission if any of the OS's comments require action.

Valid Submissions can be copied to create a new **Ongoing** one, without changing the initial Submission's state. 

####Possible transitions from this state:
- to **Invalid**: An accepted *Submission* could become **Invalid** at a later date through the *Ozone Secreatariat*'s specific action if an error in the data becomes apparent.


##6. Invalid
*Entering this state requires Ozone Secretariat input.*

Rejected submissions can be copied to create a new **Ongoing** *Submission* (revision), but the initial submission's final state will remain **Invalid**.

####Possible transitions from this state:
None.