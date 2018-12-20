import flags from '@/components/common/dataDefinitions/flags'

export default {
	name: 'flags',
	hasAssideMenu: false,
	endpoint_url: 'submission_flags_url',
	status: null,
	title: 'Flags',
	titleHtml: '<b>Flags</b>',
	tooltipHtml: '',
	detailsHtml: 'Flags',
	form_fields: flags,
	get fields_order() {
		return Object.keys(this.form_fields)
	},
	default_properties: {
		flag_provisional: false,
		flag_valid: null,
		flag_superseded: false,
		flag_checked_blanks: false,
		flag_has_blanks: false,
		flag_confirmed_blanks: false,
		flag_has_reported_a1: false,
		flag_has_reported_a2: false,
		flag_has_reported_b1: false,
		flag_has_reported_b2: false,
		flag_has_reported_b3: false,
		flag_has_reported_c1: false,
		flag_has_reported_c2: false,
		flag_has_reported_c3: false,
		flag_has_reported_e: false,
		flag_has_reported_f: false
	}
}
