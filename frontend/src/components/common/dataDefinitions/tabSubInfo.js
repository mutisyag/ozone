const getTabSubInfo = ($gettext) => {
	const tabSubInfo = {
		name: 'sub_info',
		hasAssideMenu: false,
		endpoint_url: 'sub_info_url',
		endpoint_additional_url: '',
		fields_order: ['reporting_channel', 'reporting_officer', 'designation', 'organization', 'postal_code', 'country', 'phone', 'fax', 'email', 'date'],
		intro: $gettext('Respondents are requested to read the Introduction in section 2, the General Instructions in section 4 and the Definitions in section 5 carefully before proceeding to the questionnaire and to refer to them as necessary when completing the data forms.'),
		title: $gettext('Submission Info'),
		titleHtml: `<b>${$gettext('Submission Info')}</b>`,
		detailsHtml: '',
		isInvalid: false,
		party: {
			label: $gettext('Party'),
			name: 'party',
			selected: 'China',
			type: 'text',
			validation: 'required',
			disabled: true
		},
		reporting_year: {
			label: $gettext('Reporting Period'),
			name: 'reporting_year',
			selected: '2016',
			type: 'text',
			validation: 'required',
			disabled: true
		},
		description: '',
		form_fields: {
			id: {
				selected: null
			},
			reporting_channel: {
				type: 'select',
				options: [
					{ text: $gettext('Web form'), value: 'Web form' },
					{ text: $gettext('Email'), value: 'Email' },
					{ text: $gettext('Legacy'), value: 'Legacy' },
					{ text: $gettext('Paper'), value: 'Paper' },
					{ text: $gettext('API'), value: 'API' }
				],
				selected: 'Web form'
			},
			reporting_officer: {
				type: 'text',
				selected: ''
			},
			designation: {
				type: 'text',
				selected: ''
			},
			organization: {
				type: 'text',
				selected: ''
			},
			postal_code: {
				type: 'text',
				selected: ''
			},
			country: {
				type: 'select',
				selected: '',
				optionsStatePropertyPath: 'initialData.countryOptions',
				options: []
			},
			phone: {
				type: 'text',
				selected: ''
			},
			fax: {
				type: 'text',
				selected: ''
			},
			email: {
				type: 'email',
				selected: ''
			},
			date: {
				type: 'date',
				selected: ''
			}
		},
		default_properties: {
			reporting_officer: null,
			id: null,
			designation: null,
			organization: null,
			postal_code: null,
			country: null,
			phone: null,
			fax: null,
			email: null,
			date: null,
			reporting_channel: null
		}
	}
	return tabSubInfo
}
export {
	getTabSubInfo
}
