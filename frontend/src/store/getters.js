const getters = {
	// ...
	getValidationForCurrentTab: (state) => (tab) => {
		if (['edited', false].includes(state.form.tabs[tab].status)) {
			return state.form.tabs[tab].form_fields.map(field => (field.validation.selected
				? {
					validation: field.validation.selected,
					substance: field.substance ? field.substance.selected : null,
					blend: field.blend ? field.blend.selected : null,
					facility_name: field.facility_name ? field.facility_name.selected : null
				}
				: null))
		}
	},

	getDuplicateSubmission: (state) => (data) => state.dashboard.submissions.filter(
		(sub) => sub.obligation === data.obligation
			&& sub.party === data.party
			&& sub.reporting_period === data.reporting_period
			&& sub.current_state === 'data_entry'
	),

	getSubmissionInfo: (state) => (submission) => {
		const submissionInfo = {
			obligation: () => state.dashboard.obligations.find(a => a.value === submission.obligation).text,
			period: () => {
				// TODO: find a better way to do this
				const period = state.dashboard.periods.find(a => a.value === submission.reporting_period)
				if (period && period.hasOwnProperty('text')) {
					return period.text
				}
			},
			party: () => state.dashboard.parties.find(a => a.value === submission.party).text,
			period_start: () => state.dashboard.periods.find(a => a.value === submission.reporting_period).start_date.split('-')[0],
			period_end: () => state.dashboard.periods.find(a => a.value === submission.reporting_period).end_date.split('-')[0]
		}
		return submissionInfo
	},

	getPeriodStatus: (state) => (periodId) => state.dashboard.periods.find((period) => period.value === periodId).is_reporting_open,

	checkIfBlendAlreadyEists: (state) => (blendName) => state.initialData.blends.find((blend) => blend.blend_id === blendName),

	allowedChanges: (state) => (state.current_submission ? !state.current_submission.data_changes_allowed : false)
}

export default getters