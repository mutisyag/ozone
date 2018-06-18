# Report ozone-related data

It should be possible to add & edit data through at least:
 - an upload interface that accepts data files conforming to the specific format defined by the Ozone Secretariat.
 - an interface that allows each relevant field to be added manually
 - an API (machine to machine) - this must allow chunks of partial data to be received, until completion
 - a combination of the above (e.g. a file can be uploaded and then manual field edits should be posssible)

Reporting is done via the data forms listed below (Article 7 and non-Article 7).

## Article 7 reporting

Although there are different forms for reporting different types of Article 7 data, all of it is reported together, in a single submission. Moreover, the submission contains raw data for some non-Article 7 reporting, as described [below](#reports-already-included-in-article-7-data-forms)

### List of data entry forms

TODO: link each form to the document describing in more detail the structure of the forms.

0. Questionnaire
1. Imports
2. Exports
3. Production
4. Destruction
5. Trade with non-parties
6. HFC-23 emissions

## Non-Article 7 reporting

Non-article 7 data is reported as individual submissions. There are two types of submissions: one as data-entry forms and the second as documents (narratives).

TODO: more refining needed to define the final list of reporting obligations.

### List of data entry forms

* Transfer or addition of production or consumption [Letters, ProdTransfers, ProdTransfersLetters]
* Quantities and uses of controlled substances produced and consumed for essential uses other than laboratory and analytical uses [EssenNom, EssenExemp, EssenUse]
* Quantities and uses of methyl bromide produced, imported and exported for critical uses
* Process agent uses [ProcAgentUsesDateReported, ProcAgentUsesReported]
* Consumption (imports) under the exemption for high-ambient-temperature parties (data form 7)
* Production under the exemption for high-ambient-temperature parties (data form 8)

### List of narrative reports (documents/letters)

* Licensing information
    * Establishment and operation of licensing system
    * Licensing systems for trade in controlled substances
    * Illegal trade in controlled substances 
    * Parties wishing to avoid the unwanted import of products and equipment containing or relying on hydrochlorofluorocarbons 

* Summary of activities (Article 9)

* Exemption for high ambient temperature parties

* Critical use exemptions for methyl bromide information
	* Decision Ex.I/3, paragraph 5
	* Decision Ex.I/4, paragraph 2
	* Decision Ex.I/4, paragraphs 3 and 6

TODO: the fourth category is listed above as "Quantities and uses of methyl bromide".

* Requests for changes in reported baseline data 

* Other information
	* Information relevant to international halon bank management (Decision V/15)
    * Parties supplying controlled substances to Article 5 parties 
    * List of reclamation facilities and their capacities
    * New ozone-depleting substances reported by the parties
    * Strategies on environmentally sound management of banks of ozone-depleting substances

TODO: Each bullet in its on submission?

### Reports already included in Article 7 data forms

* Controlled substance produced for laboratory and analytical uses
TODO: sometimes party report these separately and not include them in the Article 7 reports?

* Trade with non-parties (Article 4)
* Essential use exemptions: laboratory and analytical uses [LabUses]

TODO: are these a separate report as well or always included in Article 7?

# Process and manage the submitted data

TODO: describe the use-cases related to processing:

* aggregation for each group of substances
* calculations of ODP and GWP tons
* analyzing the status of compliance [DeviationTypes, DeviationSources]

TODO: how much of these can be automatized?

TODO: comparison with previous periods during processing?

# Account management

As any user, I should be able to:

- reset my password
- receive a notification when my account is created, blocked, de-activated or when my password is reset by an administrator
- authenticate using the same credentials to the ORS and to the Ozone Secretariat website


# Lookup tables for parties

As a Party, I should have read-only access to the following information:

	1.	Controlled substances (Annex, Group, Name, ODP, Formula, Number of Isomers, MinODP, MaxO DP)
		a.	Controlled HFCs
		b.	Controlled HCFCs
	2.	Blends containing controlled substances (Name, Other Names, Components, Percentage)
		a.	Blends containing HCFCs
		b.	Blends containing HFCs
		c.	Blends containing CFCs
	3.	Parties (Name, Region, A5 status, EU Membership, Ratification Dates and Types for each treaty and amendment)
		a.	Article 5 Parties (exclude field for A5 status and EU membership)
		b.	Non-Article 5 Parties (exclude field for A5 status)
		c.	EU member states (Name, Date of joining EU)
		d.	Parties to the Kigali Amendment (Name, , Ratification Date and Type for Kigali amendment)

# Lookup tables for the Ozone Secretariat

TODO

