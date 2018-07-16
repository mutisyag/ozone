# 1. Creating new submissions

Submissions can be created both by Party and Secretariat users.

## 1.1 Creating a submission from scratch

Steps:
- Secretariat-only: choosing the Party for which the data will be reported
- choosing the obligation to be reported on (based on the Party's relevant obligations)
- choosing the reporting period (default will be current) based on what is available for the obligation
- if the Party-Obligation-Period already has data, the ORS will warn the user and will present the option of creating a submission based on that existing data (treated at point 1.2)
- filling in the data (form completion or uploading data file)
- setting the submission flags
- pressing the Submit button - this will trigger a popup telling the user that the data will be considered final

Until the last step (pressing the Submit button), the data can be modified freely. Any change will be recorded by the ORS, and will be persistent upon user session expiry, but it will be visible only to the user.


## 1.2 Creating a submission based on existing data

In this case, the user wants to start a new submission based on previously-reported data, with a limited number of changes.

Steps:
- Secretariat-only: choosing the Party for which the data will be reported
- choosing the obligation to be reported on (based on the Party's relevant obligations)
- choosing the reporting period (default will be current) based on what is available for the obligation
- choosing which version of existing data will be replicated. User will be presented with all non-recalled submissions from the Party-Obligation-Period to choose from. Default choice will be the submission marked as "current" in the ORS. 
- user will be prompted to confirm the selected version. After that, the forms will be pre-populated with the existing values 
- user can change any of the pre-populated fields in the form
- setting the Provisional/Incomplete flags 
- pressing the Submit button - this will trigger a popup telling the user that the data will be considered final
Until the last step (pressing the Submit button), the data can be modified freely. Any change will be recorded by the ORS, and will be persistent upon user session expiry, but it will be visible only to the user.
After pressing the Submit button, a new submission will be created. It will be considered as the "current" submission for its Party-Obligation-Period combination.

Alternatively, the user can view (point 3) the submission he wants to change, then select the "Create new submission based on this" option.   


# 2. Changing submitted data

Once submitted, existing submissions cannot be changed, but new ones can be created based on them. The newly-created submissions will be in *Data Entry* state and can be edited as needed.

If any user wants to change some already-submitted data, he can follow the steps at point 1.2.


# 3. Viewing submissions

Secretariat users can view any submission from any Party.

Party users can see any of that Party's submissions.

Steps:
- Secretariat-only: choose a Party from the parties list
- at this point, optionally, the user will be able to directly choose a specific submissions from a "Recent Submissions" list for that Party
- choose an Obligation from the specific party's obligations list
- at this point, optionally, the user will be able to directly choose a specific submissions from a "Recent Submissions for obligation" list for that Party-Obligation pair
- choose a Reporting Period for that obligation
- at this point, the user will be presented with the complete list of submissions for that Party-Obligation-Period combination
- after that, the user will be able to select one submission from this list and view its details.

When presenting the list of submissions, each submission will be marked (color, font) according to its state.

The current submission for that Party-Obligation-Period combination will be visibly marked.


# 3.1 Viewing the submissions history for a specific Party-Obligation-Period combination

The process will be identical with the steps for point 3.

Submissions will be presented in a list in chronological order, with the exception of the recalled ones, which will be presented separately.

Note: Chronological order makes sense since the current submission is always the last unrecalled one.


# 3.2 Viewing submission details

When accessing a specific submission, its details are available for all users who have the right to view it.

The following details will be available:
- all reporting data for that submission
- date of creation
- user who created the submission
- current submission state
- all submission flags
- history of all state & flag changes - with timestamps and users who performed them 


# 4. Processing submissions

This feature is available only for Secretariat users.

At any point, the user will be able to select for processing only the submissions that are "current" (i.e. not marked as superseded). Also, any submissions list presented to the user will only contain current submissions.

Steps:
- optionally, user will be able to see a list of the most recent current submissions for all Parties and directly pick one of them
- choose a Party from the parties list
- choose an Obligation from the specific party's obligations list
- choose a Reporting Period for that obligation; default will be the current reporting period
- at this point, the user will be taken directly to the current submission for that Party-Obligation-Period combination
- user will have to press the "Processing" button to change the state of the submission to "Processing"
- do the actual processing
TODO: anything else to be added here?

When a submission in processing is being recalled, user will be notified and will receive a direct link to the submission that has now become "current" for the Party-Obligation-Period combination. 


# 5. Recalling submissions

This is a Party-only feature.

If a Party decides that a submission is incorrect, they can choose to recall that submission regardless of its current state.

Recalling is done by navigating to that specific submission and pressing the "Recall" button.

Steps are identical to those at point 3 (viewing). Once selecting the desired submission, user will be able to press a "Recall" button, which will trigger a confirmation step.

However, any submission list presented to the user will only contain current submissions (non-current ones cannot be recalled).
 
Since recalling a current submission makes the previous (unrecalled) one current, the user will be notified clearly about which submission becomes current in this case. 


# 6. Re-instating recalled submissions

This is a Party-only feature.

Reinstating is done by navigating to that specific submission and pressing the "Reinstate" button.


# 7. Reverting to previous submissions

When a submission contains errors, it is possible to revert to a previous one that is considered good.

To keep the submissions history clean, this can be done by creating a new submission based on existing data (point 1.1) and leaving its data unmodified.

This can also be done as a side effect of the following actions:
- recalling (point 5) - which will automatically set the previous submission as current
- re-instating a recalled submission (point 6) - which will set the re-instated submission as current


# 8. Validating submissions

This feature is available only for Secretariat users.

