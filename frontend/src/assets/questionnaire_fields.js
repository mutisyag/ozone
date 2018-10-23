// import 'promise-polyfill/src/polyfill';



export const intro_fields = [
	{
		label: '1.1. Did your country import CFCs, halons, carbon tetrachloride, methyl chloroform, HCFCs, HBFCs, bromochloromethane, or methyl bromide in the reporting year?',
		type: 'radio',
		name: 'has_imports',
		selected: true,
		options: [{text: 'Yes', value: true},{text: 'No', value: false}],
		info:'If No, ignore data form 1 and go to question 1.2. If Yes, please complete data form 1. Please read Instruction I of the document carefully before filling in the form.',
	},
	{
		label: '1.2. Did your country export or re-export CFCs, halons, carbon tetrachloride, methyl chloroform, HCFCs, HBFCs, bromochloromethane, or methyl bromide in the reporting year?',
		type: 'radio',
		name: 'has_exports',
		selected: true,
		options: [{text: 'Yes', value: true},{text: 'No', value: false}],
		info: 'If No, ignore data form 2 and go to question 1.3. If Yes, please complete data form 2. Please read Instruction II of the document carefully before filling in the form.'
	},
	{
		label: '1.3. Did your country produce CFCs, halons, carbon tetrachloride, methyl chloroform, HCFCs, HBFCs, bromochloromethane, or methyl bromide in the reporting year?',
		type: 'radio',
		name: 'has_produced',
		selected: true,
		options: [{text: 'Yes', value: true},{text: 'No', value: false}],
		info: 'If No, ignore data form 3 and go to question 1.4. If Yes, please complete data form 3. Please read Instruction III of the document carefully before filling in the form.'
	},	
	{
		label: '1.4. Did your country destroy any ODSs in the reporting year?',
		type: 'radio',
		name: 'has_destroyed',
		selected: true,
		options: [{text: 'Yes', value: true},{text: 'No', value: false}],
		info: 'If No, ignore data form 4 and go to question 1.5. If Yes, please complete data form 4. Please read Instruction IV of the document carefully before filling in the form.'
	},		
	{
		label: '1.5. Did your country import from or export or re-export to non-Parties in the reporting year?',
		type: 'radio',
		name: 'has_nonparty',
		selected: null,
		options: [{text: 'Yes', value: true},{text: 'No', value: false}],
		info: 'If No, ignore data form 5. If Yes, please complete data form 5. Please read Instruction V of the document carefully, and, particularly, the definition of non-Parties before filling in the form.'
	},
	{
		label: '1.6. DATA ON GENERATION OF HFC 23 FROM FACILITIES MANUFACTURING ANNEX C GROUP I OR ANNEX F SUBSTANCES ?',
		type: 'radio',
		name: 'has_emissions',
		selected: true,
		options: [{text: 'Yes', value: true},{text: 'No', value: false}],
		info: 'If No, ignore data form 5. If Yes, please complete data form 5. Please read Instruction V of the document carefully, and, particularly, the definition of non-Parties before filling in the form.'
	},		
]


export const reporting_party = [
	{
		label: 'Name of reporting officer',
		name: 'reporting_officer',
		type: 'text',
		selected: 'test',
		validation: 'required',
	},
	{
		label: 'Designation',
		name: 'designation',
		type: 'text',
		selected: 'test',
		validation: 'required'
	},
	{
		label: 'Organization',
		name: 'organization',
		type: 'text',
		selected: 'test',
		validation: 'required'
	},
	{
		label: 'Postal Adddress',
		name: 'postal_address',
		type: 'text',
		selected: 'test',
		validation: 'required'
	},
	{
		label: 'Country',
		name: 'country',
		type: 'text',
		selected: 'test',
		validation: 'required|alpha'
	},
	{
		label: 'Phone',
		name: 'phone',
		type: 'text',
		selected: 'test',
		validation: 'required'
	},
	{
		label: 'Fax',
		name: 'fax',
		type: 'text',
		selected: 'test',
		validation: 'required'
	},
	{
		label: 'E-mail',
		name: 'mail',
		type: 'email',
		selected: 'test@test.test',
		validation: 'required|email'
	},
	{
		label: 'Date',
		name: 'date',
		type: 'date',
		selected: '2018-02-05',
		validation: 'required'
	}
]





 






