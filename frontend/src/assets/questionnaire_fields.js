// import 'promise-polyfill/src/polyfill';



export const intro_fields = [
	{
		label: '1.1. Did your country import CFCs, halons, carbon tetrachloride, methyl chloroform, HCFCs, HBFCs, bromochloromethane, or methyl bromide in the reporting year?',
		type: 'radio',
		name: 'import_question',
		selected: true,
		options: [{text: 'Yes', value: true},{text: 'No', value: false}],
		info:'If No, ignore data form 1 and go to question 1.2. If Yes, please complete data form 1. Please read Instruction I of the document carefully before filling in the form.',
	},
	{
		label: '1.2. Did your country export or re-export CFCs, halons, carbon tetrachloride, methyl chloroform, HCFCs, HBFCs, bromochloromethane, or methyl bromide in the reporting year?',
		type: 'radio',
		name: 'export_question',
		selected: true,
		options: [{text: 'Yes', value: true},{text: 'No', value: false}],
		info: 'If No, ignore data form 2 and go to question 1.3. If Yes, please complete data form 2. Please read Instruction II of the document carefully before filling in the form.'
	},
	{
		label: '1.3. Did your country produce CFCs, halons, carbon tetrachloride, methyl chloroform, HCFCs, HBFCs, bromochloromethane, or methyl bromide in the reporting year?',
		type: 'radio',
		name: 'production_question',
		selected: null,
		options: [{text: 'Yes', value: true},{text: 'No', value: false}],
		info: 'If No, ignore data form 3 and go to question 1.4. If Yes, please complete data form 3. Please read Instruction III of the document carefully before filling in the form.'
	},	
	{
		label: '1.4. Did your country destroy any ODSs in the reporting year?',
		type: 'radio',
		name: 'destruction_question',
		selected: null,
		options: [{text: 'Yes', value: true},{text: 'No', value: false}],
		info: 'If No, ignore data form 4 and go to question 1.5. If Yes, please complete data form 4. Please read Instruction IV of the document carefully before filling in the form.'
	},		
	{
		label: '1.5. Did your country import from or export or re-export to non-Parties in the reporting year?',
		type: 'radio',
		name: 'nonparty_question',
		selected: null,
		options: [{text: 'Yes', value: true},{text: 'No', value: false}],
		info: 'If No, ignore data form 5. If Yes, please complete data form 5. Please read Instruction V of the document carefully, and, particularly, the definition of non-Parties before filling in the form.'
	},			
]


export const reporting_party = [
	{
		label: 'Name of reporting officer',
		name: 'reporting_officer',
		type: 'text',
		selected: '',
		validation: 'required',
	},
	{
		label: 'Designation',
		name: 'designation',
		type: 'text',
		selected: '',
		validation: 'required'
	},
	{
		label: 'Organization',
		name: 'organization',
		type: 'text',
		selected: '',
		validation: 'required'
	},
	{
		label: 'Postal Adddress',
		name: 'postal_address',
		type: 'text',
		selected: '',
		validation: 'required'
	},
	{
		label: 'Country',
		name: 'country',
		type: 'text',
		selected: '',
		validation: 'required|alpha'
	},
	{
		label: 'Phone',
		name: 'phone',
		type: 'text',
		selected: '',
		validation: 'required'
	},
	{
		label: 'Fax',
		name: 'fax',
		type: 'text',
		selected: '',
		validation: 'required'
	},
	{
		label: 'E-mail',
		name: 'mail',
		type: 'email',
		selected: '',
		validation: 'required|email'
	},
	{
		label: 'Date',
		name: 'date',
		type: 'date',
		selected: null,
		validation: 'required'
	}
]





 






