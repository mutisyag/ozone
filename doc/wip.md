Internal notes and work in progress
===================================



# Use cases: 

As a member of the OS, I want to be able to view all submitted data.
Reporters should be able to view a history of their Party's submissions.

Some parties are not obliged to report on some annex groups

A submitted report requires changes

Secretariat needs to continue the reporter's data entry

View any past submission available in the system.

A Party changes Article 5 status

Change of ratification status

Change of baseline

Delete ongoing data entry report

OS enter data on behalf of a Party

Time out and log out when inactive for 10 minutes. Any ongoing unsaved edits are saved first.

Trigger automatic warnings when certain predefined limits are exceeded on specific fields.

Admin: view change log for any submission



# Article 7 form details

Each dataform should have its own tab. The user should be able to easily switch/navigate between tabs and separately save the data entered on each of these.

Each submission will be tied to a reporting period; the Party will be able to select the period to report on in the interface, with the default being the current reporting period (*rules are in fact more complex; to be written down*).

The interface should display workflow progress and state to the reporter, for example in a process-like illustration.

# EU
	production is reported by country
	consumption is reported for the entire EU aggregated
	- for the EU, the production is not calculated
	- for EU member states, the consumption is not calculated [tbl_ProdCons]

# Blends

- a simulator for blends/mixtures
- described in terms of percentages of pure substances
- there is a list of blends
- known blends - percentages that everyone agrees
- calculate the quantities of pure substances
- ideally during the data entry phase - show the different components above
- production is usually just pure substances
- destroy - non standard blends
	- recovered from equipment
	- different percentages


# Data migration

