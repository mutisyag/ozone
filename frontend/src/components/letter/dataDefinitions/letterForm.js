const form = {
	formDetails: {
		dataNeeded: [
		]
	},
	tabs: {
		sub_info: {
			name: 'sub_info',
			endpoint_url: 'sub_info_url',
			endpoint_additional_url: '',
			fields_order: ['reporting_officer', 'designation', 'organization', 'postal_code', 'country', 'phone', 'fax', 'email', 'date'],
			intro: 'Respondents are requested to read the Introduction in section 2, the General Instructions in section 4 and the Definitions in section 5 carefully before proceeding to the questionnaire and to refer to them as necessary when completing the data forms.',
			title: 'Submission Info',
			titleHtml: 'Submission Info',
			detailsHtml: '',
			isInvalid: false,
			party: {
				label: 'Party',
				name: 'party',
				selected: 'China',
				type: 'text',
				validation: 'required',
				disabled: true
			},
			reporting_year: {
				label: 'Reporting Period',
				name: 'reporting_year',
				selected: '2016',
				type: 'text',
				validation: 'required',
				disabled: true
			},
			description: '',
			form_fields: [],
			default_properties: {
				reporting_officer: null,
				designation: null,
				organization: null,
				postal_code: null,
				country: null,
				phone: null,
				fax: null,
				email: null,
				date: null
			}
		},
		attachments: {
			name: 'attachments',
			title: 'Attachments',
			titleHtml: 'Attachments',
			detailsHtml: ''
		}
	}
}
export default form
