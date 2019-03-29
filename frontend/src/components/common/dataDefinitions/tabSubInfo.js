const getTabSubInfo = ($gettext) => {
	const tabSubInfo = {
		name: 'sub_info',
		hasAssideMenu: false,
		status: null,
		validate: true,
		endpoint_url: 'sub_info_url',
		endpoint_additional_url: '',
		fields_order: ['reporting_channel', 'submission_format', 'reporting_officer', 'designation', 'organization', 'postal_address', 'country', 'phone', 'email', 'date'],
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
				selected: '',
				validation: null
			},
			designation: {
				type: 'text',
				selected: ''
			},
			organization: {
				type: 'text',
				selected: ''
			},
			postal_address: {
				type: 'textarea',
				selected: '',
				validation: null
			},
			country: {
				type: 'select',
				selected: '',
				optionsStatePropertyPath: 'initialData.countryOptionsSubInfo',
				options: []
			},
			submission_format: {
				type: 'select',
				selected: '',
				optionsStatePropertyPath: 'initialData.submissionFormats',
				selectedPropertyPath: 'submissionDefaultValues.submission_format',
				options: [],
				permission: 'is_secretariat'
			},
			phone: {
				type: 'text',
				selected: ''
			},
			email: {
				type: 'email',
				selected: '',
				validation: null
			},
			date: {
				type: 'date',
				selected: '',
				tooltip: $gettext('The date indicated on the submitted document')
			},
			submitted_at: {
				type: 'date',
				selected: ''
			},
			get validation() {
				const invalid = []
				if (!this.reporting_officer.selected) {
					this.reporting_officer.validation = $gettext('Required')
					invalid.push($gettext('Reporting officer'))
				} else {
					this.reporting_officer.validation = null
				}

				if (!this.postal_address.selected && !this.email.selected) {
					this.postal_address.validation = $gettext('Required')
					this.email.validation = $gettext('Required')
					invalid.push($gettext('Email/Address'))
				} else {
					this.postal_address.validation = null
					this.email.validation = null
				}

				if (this.submitted_at.validation) {
					// This is a special case because this field is required only for secretariat users and validation property is set from outside
					invalid.push($gettext('Date of submission'))
				}

				return {
					selected: invalid
				}
			}
		},
		default_properties: {
			reporting_officer: null,
			id: null,
			designation: null,
			submission_format: null,
			organization: null,
			postal_address: null,
			country: null,
			phone: null,
			email: null,
			date: null,
			submitted_at: null,
			reporting_channel: null
		}
	}
	return tabSubInfo
}
export {
	getTabSubInfo
}
