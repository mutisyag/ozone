const getCommonLabels = ($gettext) => {
	const labels = {
		__all__: '',
		comments_party: $gettext('Party'),
		comments_secretariat: $gettext('Secretariat'),
		recall: $gettext('Recall'),
		process: $gettext('Process'),
		finalize: $gettext('Finalize'),
		submit: $gettext('Submit'),
		other: $gettext('Other'),
		unrecall_to_submitted: $gettext('Reinstate'),
		unrecall_to_processing: $gettext('Reinstate'),
		unrecall_to_finalized: $gettext('Reinstate'),
		reporting_officer: $gettext('Name of reporting officer'),
		designation: $gettext('Designation'),
		organization: $gettext('Organization'),
		postal_code: $gettext('Postal code'),
		postal_address: $gettext('Postal address'),
		country: $gettext('Country'),
		phone: $gettext('Phone'),
		reporting_channel: $gettext('Reporting channel'),
		email: $gettext('E-mail'),
		date: $gettext('Date'),
		submitted_at: $gettext('Date of submission'),
		art7: $gettext('Article 7'),
		hat: $gettext('HAT'),
		submission_format: $gettext('Submission format'),
		valid: $gettext('valid'),
		invalid: $gettext('invalid'),
		questionnaire_remarks_party: $gettext('Comments (Party)'),
		questionnaire_remarks_secretariat: $gettext('Comments (Secretariat)'),
		edit: $gettext('Edit'),
		view: $gettext('View'),
		revise: $gettext('Revise'),
		delete: $gettext('Delete'),
		flags: {
			flag_superseded: $gettext('Superseded'),
			flag_provisional: $gettext('Provisional'),
			flag_checked_blanks: $gettext('Checked blanks'),
			flag_has_blanks: $gettext('Has blanks'),
			flag_valid: $gettext('Valid'),
			flag_confirmed_blanks: $gettext('Confirmed blanks'),
			flag_has_reported_a1: $gettext('A/I'),
			flag_has_reported_a2: $gettext('A/II'),
			flag_has_reported_b1: $gettext('B/I'),
			flag_has_reported_b2: $gettext('B/II'),
			flag_has_reported_b3: $gettext('B/III'),
			flag_has_reported_c1: $gettext('C/I'),
			flag_has_reported_c2: $gettext('C/II'),
			flag_has_reported_c3: $gettext('C/IIII'),
			flag_has_reported_e: $gettext('E/I'),
			flag_has_reported_f: $gettext('F')
		}
	}
	return labels
}

export {
	getCommonLabels
}
