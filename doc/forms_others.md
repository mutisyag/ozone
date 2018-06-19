# Forms for non-article 7 reporting


## 1. Transfer or addition of production or consumption

### 1.1 Existing tables in the current database:

* Letters
* ProdTransfers
* ProdTransfersLetters

### 1.2 Parties to complete these forms

* Transfer of production: any parties; both parties involved 
* Transfer of consumption: non-article 5 parties; both parties involved

### 1.3 Frequency of reporting

Reported whenever such a transfer/addition happens.
The period for which the transfer applies should be stated.

### 1.4 Structure

The product transfer forms should allow new product transfers to be created by the Ozone Secretariat as needed and associated with the relevant letters, which are stored in a separate Database table.

Each product transfer form should have the following fields:

* Letter - multiple choice field; mandatory; references a Letters table; each transfer can have multiple letters
* Substance - multiple choice field; mandatory; references a Substances table
* Period - multiple choice field; mandatory; references a Periods table
* Originating Country - multiple choice field; mandatory; references a Countries table
* Destination Country - multiple choice field; mandatory; references a Countries table
* Transfer quantity - numerical value in metric tons; mandatory
* Production Transfer Used - numerical value in metric tons; not mandatory
* Is Basic Domestic Need? - True/False; not mandatory
* Remarks - free form text field; not mandatory

For each registered product transfer, the OS should be able to associate the relevant transfer letter(s) (each transfer may be documented by both the originating and the destination country).

Notes:
* annex and group, present in the current data tables, will be stored separately in the substances table, per substance

### 1.5 Processing by the secretariat

TBD

### 1.6 Questions

* it seems like only production transfers are being recorded (no consumption transfers, no additions). Is this correct?
* not sure what about the "Is Basic Domestic Need" field meaning



## 2. Quantities and uses of controlled substances produced and consumed for essential uses other than laboratory and analytical uses

### 2.1 Existing tables in the current database:

* EssenNom
* EssenExemp
* EssenUse

### 2.2 Parties to complete these forms

Any party, if it received an exemption

### 2.3 Frequency of reporting

Reported the year following an exemption.

Report should be completed in the approved format by 31 January of each year.

### 2.4 Structure

Reporting data for this will comprise several forms:

#### 2.4.1 Essential Use Nominations

Each nomination will be reported by the Ozone Secretariat in a form comprised of the following fields:


#### 2.4.2 Essential Use Exemptions

Each exemption will be reported by the Ozone Secretariat in a form comprised of the following fields:

* Country - multiple choice field; mandatory; references a Countries table
* Period for Exemption - mutiple choice field; mandatory; references a Periods table
* Substance - multiple choice field; mandatory; references a Substances table
* Approval Decision - multiple choice field; mandatory; references a Decisions table
* Quantity approved by the TEAP - numerical; not mandatory; metric tonnes
* Approved Amount - numerical; metric tonnes; mandatory; pre-populated with `Quantity approved by the TEAP` value, if that was filled in
* Type - multiple choice field; not mandatory; possible values are 'Essential' and 'Critical'
* Is emergency - True/False; not mandatory
* Remark - free-form text field; not mandatory

Notes:
* TEAP - Technological and Economic Assessment Panel

#### 2.4.3 Essential Uses

Each essential use will be reported by the Party (or by the Ozone Secretariat) in a form comprised of the following fields:


### 2.5 Processing by the secretariat


### 2.6 Questions



## 3. Quantities and uses of methyl bromide produced, imported and exported for critical uses

### 3.1 Existing tables in the current database:

* MeBrAgreedCriticalUseCategories
* MeBrActualCriticalUseByCategory

Note:
* just as a side note, essential (not critical!) uses for Methyl Bromide are in the EssenUse... tables with substance ID 194 

### 3.2 Parties to complete these forms

Any party, if it received a critical use exemption

### 3.3 Frequency of reporting

Reported once for each critical use exemption

### 3.4 Structure

Reporting data for this will comprise several forms:

#### 3.4.1 Agreed critical uses

Each agreed critical use will be reported by the Ozone Secretariat in a form comprised of the following fields:

* Country - multiple choice field; mandatory; references a Countries table
* Period for Exemption - mutiple choice field; mandatory; references a Periods table
* Approval Decision - multiple choice field; mandatory; references a Decisions table
* Categories of permitted critical uses - free-form text field; mandatory
* Approved Amount - numerical; metric tonnes; mandatory

#### 3.4.2 Actual critical uses

Each actual critical use will be reported by the Party (or by the Secretariat) in a form comprised of the following fields:

* Country - multiple choice field; mandatory; references a Countries table
* Period for Exemption - mutiple choice field; mandatory; references a Periods table
* Critical Use Title - free-form text field; mandatory
* Critical Use Amount - numerical; metric tonnes; mandatory
* Remark - free-form text field; not mandatory

### 3.5 Processing by the secretariat

### 3.6 Questions

* Is there any restriction to be placed on the `Categories of permitted critical uses` field?



## 4. Process agent uses 

### 4.1 Existing tables in the current database:

* ProcAgentUsesDateReported (?)
* ProcAgentUsesReported

### 4.2 Parties to complete these forms

Any party

### 4.3 Frequency of reporting

Reported annually

### 4.4 Structure

Each process agent use will be reported by the Party (or by the Secretariat) in a form comprised of the following fields:

* Country - multiple choice field; mandatory; references a Countries table
* Period - mutiple choice field; mandatory; references a Periods table
* Decision - multiple choice field; mandatory; references a Decisions table
* Process Number - numerical; non-mandatory
* Approved Amount - numerical; metric tonnes; mandatory
* Emissions - numerical; not mandatory
* Units - multiple choice field; mandatory if Emissions field is filled; possible values: Metric Tonnes, ODP Tonnes
* Remark - free-form text field; not mandatory

### 4.5 Processing by the secretariat

### 4.6 Questions

* do not understand the meaning of the `Process Number` field in ProcAgentUsesReported
* the Decision field in ProcAgentUsesReported has 2 values for one row (ID 140); is this correct?
* Data in the ProcAgentUsesDateReported seems to miss links with other tables 
* Not sure how the data from the two tables can be aggregated (no ID/country match etc)
* Not sure how the ProcAgentUses table in the existing data fits into this, but it seems redundant/obsolete



## 5. Consumption (imports) under the exemption for high-ambient-temperature parties (data form 7)

### 5.1 Existing tables in the current database:

### 5.2 Parties to complete these forms

Parties listed in Decision XXVIII/2 (Algeria, Bahrain, Benin, Burkina Faso, Central African Republic, Chad, Côte d'Ivoire, Djibouti, Egypt, Eritrea,
Gambia, Ghana, Guinea, Guinea-Bissau, Iran (Islamic Republic of), Iraq, Jordan, Kuwait, Libya, Mali,
Mauritania, Niger, Nigeria, Oman, Pakistan, Qatar, Saudi Arabia, Senegal, Sudan, Syrian Arab Republic, Togo,
Tunisia, Turkmenistan, United Arab Emirates).

### 5.3 Frequency of reporting

Reported the year following an exemption

### 5.4 Structure

Exemption subsectors:
(a) Multi-split air conditioners (commercial and residential)
(b) Split ducted air conditioners (commercial and residential)
(c) Ducted commercial packaged (self-contained) air-conditioners

### 5.5 Processing by the secretariat



## 6. Production under the exemption for high-ambient-temperature parties (data form 8)

### 6.1 Existing tables in the current database:

### 6.2 Parties to complete these forms

Parties listed in Decision XXVIII/2 (Algeria, Bahrain, Benin, Burkina Faso, Central African Republic, Chad, Côte d'Ivoire, Djibouti, Egypt, Eritrea,
Gambia, Ghana, Guinea, Guinea-Bissau, Iran (Islamic Republic of), Iraq, Jordan, Kuwait, Libya, Mali,
Mauritania, Niger, Nigeria, Oman, Pakistan, Qatar, Saudi Arabia, Senegal, Sudan, Syrian Arab Republic, Togo,
Tunisia, Turkmenistan, United Arab Emirates).

### 6.3 Frequency of reporting

Reported the year following an exemption

### 6.4 Structure

Exemption subsectors:
(a) Multi-split air conditioners (commercial and residential)
(b) Split ducted air conditioners (commercial and residential)
(c) Ducted commercial packaged (self-contained) air-conditioners

### 6.5 Processing by the secretariat