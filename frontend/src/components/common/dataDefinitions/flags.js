export default {
	flag_provisional: {
		selected: true,
		type: 'checkbox',
		disabled: true,
		tooltip: 'Another report will need to be submitted with the final data'
	},
	flag_valid: {
		selected: false,
		type: 'checkbox',
		options: [
			{ text: 'Submission is valid', value: true },
			{ text: 'Submission is not valid', value: false }
		],
		radioType: 'stacked',
		disabled: true
	},
	flag_superseded: {
		selected: false,
		type: 'checkbox',
		disabled: true
	},
	flag_checked_blanks: {
		selected: false,
		type: 'checkbox',
		disabled: true
	},
	flag_has_blanks: {
		selected: false,
		type: 'checkbox',
		disabled: true
	},
	flag_confirmed_blanks: {
		selected: true,
		type: 'checkbox',
		disabled: true
	},
	flag_has_reported_a1: {
		selected: false,
		type: 'checkbox',
		disabled: true
	},
	flag_has_reported_a2: {
		selected: false,
		type: 'checkbox',
		disabled: true
	},
	flag_has_reported_b1: {
		selected: false,
		type: 'checkbox',
		disabled: true
	},
	flag_has_reported_b2: {
		selected: false,
		type: 'checkbox',
		disabled: true
	},
	flag_has_reported_b3: {
		selected: false,
		type: 'checkbox',
		disabled: true
	},
	flag_has_reported_c1: {
		selected: false,
		type: 'checkbox',
		disabled: true
	},
	flag_has_reported_c2: {
		selected: false,
		type: 'checkbox',
		disabled: true
	},
	flag_has_reported_c3: {
		selected: false,
		type: 'checkbox',
		disabled: true
	},
	flag_has_reported_e: {
		selected: false,
		type: 'checkbox',
		disabled: true
	},
	flag_has_reported_f: {
		selected: false,
		type: 'checkbox',
		disabled: true
	},
	get validation() {
		if (!this.flag_checked_blanks.selected) {
			this.flag_has_blanks.disabled = true
			this.flag_confirmed_blanks.disabled = true
			this.flag_has_blanks.selected = false
			this.flag_confirmed_blanks.selected = false
		} else {
			this.flag_has_blanks.disabled = false
		}
		if (!this.flag_has_blanks.selected) {
			this.flag_confirmed_blanks.disabled = true
			this.flag_confirmed_blanks.selected = false
		} else {
			this.flag_confirmed_blanks.disabled = false
		}
		return {}
	}
}
