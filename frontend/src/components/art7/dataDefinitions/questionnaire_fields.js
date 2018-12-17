export const intro_fields = {
	has_imports: {
		label: '1. Did your country import CFCs, halons, carbon tetrachloride, methyl chloroform, HCFCs, HBFCs, bromochloromethane, or methyl bromide in the reporting year?',
		type: 'radio',
		name: 'has_imports',
		selected: null,
		options: [{ text: 'Yes', value: true }, { text: 'No', value: false }],
		info: 'If No, ignore data form 1 and go to question 1.2. If Yes, please complete data form 1. Please read Instruction I of the document carefully before filling in the form.'
	},
	has_exports: {
		label: '2. Did your country export or re-export CFCs, halons, carbon tetrachloride, methyl chloroform, HCFCs, HBFCs, bromochloromethane, or methyl bromide in the reporting year?',
		type: 'radio',
		name: 'has_exports',
		selected: null,
		options: [{ text: 'Yes', value: true }, { text: 'No', value: false }],
		info: 'If No, ignore data form 2 and go to question 1.3. If Yes, please complete data form 2. Please read Instruction II of the document carefully before filling in the form.'
	},
	has_produced: {
		label: '3. Did your country produce CFCs, halons, carbon tetrachloride, methyl chloroform, HCFCs, HBFCs, bromochloromethane, or methyl bromide in the reporting year?',
		type: 'radio',
		name: 'has_produced',
		selected: null,
		options: [{ text: 'Yes', value: true }, { text: 'No', value: false }],
		info: 'If No, ignore data form 3 and go to question 1.4. If Yes, please complete data form 3. Please read Instruction III of the document carefully before filling in the form.'
	},
	has_destroyed: {
		label: '4. Did your country destroy any ODSs in the reporting year?',
		type: 'radio',
		name: 'has_destroyed',
		selected: null,
		options: [{ text: 'Yes', value: true }, { text: 'No', value: false }],
		info: 'If No, ignore data form 4 and go to question 1.5. If Yes, please complete data form 4. Please read Instruction IV of the document carefully before filling in the form.'
	},
	has_nonparty: {
		label: '5. Did your country import from or export or re-export to non-Parties in the reporting year?',
		type: 'radio',
		name: 'has_nonparty',
		selected: null,
		options: [{ text: 'Yes', value: true }, { text: 'No', value: false }],
		info: 'If No, ignore data form 5. If Yes, please complete data form 5. Please read Instruction V of the document carefully, and, particularly, the definition of non-Parties before filling in the form.'
	},
	has_emissions: {
		label: '6. Did your country generate the substance HFC23 in the reporting year from any facility that produces (manufactures) Annex C Group I or Annex F substances?',
		type: 'radio',
		name: 'has_emissions',
		selected: null,
		options: [{ text: 'Yes', value: true }, { text: 'No', value: false }],
		info: 'If No, ignore data form 5. If Yes, please complete data form 5. Please read Instruction V of the document carefully, and, particularly, the definition of non-Parties before filling in the form.'
	}
}
