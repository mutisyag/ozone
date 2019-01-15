const getLabels = ($gettext) => {
	const labels = {
		__all__: '',
		comments_party: $gettext('Party'),
		comments_secretariat: $gettext('Secretariat'),
		recall: $gettext('Recall'),
		process: $gettext('Process'),
		finalize: $gettext('Finalize'),
		submit: $gettext('Submit'),
		unrecall_to_submitted: $gettext('Reinstate'),
		unrecall_to_processing: $gettext('Reinstate'),
		unrecall_to_finalized: $gettext('Reinstate'),
		reporting_officer: $gettext('Name of reporting officer'),
		designation: $gettext('Designation'),
		organization: $gettext('Organization'),
		postal_code: $gettext('Postal adddress'),
		country: $gettext('Country'),
		phone: $gettext('Phone'),
		reporting_channel: $gettext('Reporting channel'),
		fax: $gettext('Fax'),
		email: $gettext('E-mail'),
		date: $gettext('Date'),
		dateOfSubmission: $gettext('Date of submission'),
		subject: $gettext('Subject'),
		art7: $gettext('Article 7'),
		hat: $gettext('HAT'),
		valid: $gettext('valid'),
		invalid: $gettext('invalid'),
		flags: {
			flag_superseded: $gettext('Superseded'),
			flag_provisional: $gettext('Provisional'),
			flag_checked_blanks: $gettext('Checked blanks'),
			flag_has_blanks: $gettext('Has blanks'),
			flag_valid: $gettext('Valid'),
			flag_confirmed_blanks: $gettext('Confirmed blanks'),
			flag_has_reported_a1: $gettext('Annex group A1'),
			flag_has_reported_a2: $gettext('Annex group A2'),
			flag_has_reported_b1: $gettext('Annex group B1'),
			flag_has_reported_b2: $gettext('Annex group B2'),
			flag_has_reported_b3: $gettext('Annex group B3'),
			flag_has_reported_c1: $gettext('Annex group C1'),
			flag_has_reported_c2: $gettext('Annex group C2'),
			flag_has_reported_c3: $gettext('Annex group C3'),
			flag_has_reported_e: $gettext('Annex group E'),
			flag_has_reported_f: $gettext('Annex group F')
		}
	}
	return labels
}

export {
	getLabels
}
