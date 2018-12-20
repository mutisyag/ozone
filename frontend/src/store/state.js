const state = {
	dashboard: {
		mySubmissions: null,
		submissions: null,
		periods: null,
		obligations: null,
		parties: null,
		table: {
			currentPage: 1,
			perPage: 10,
			totalRows: null,
			sorting: {
				sortBy: 'updated_at',
				sortDesc: true,
				sortDirection: 'asc'
			},
			filters: {
				search: null,
				period_start: null,
				period_end: null,
				obligation: null,
				party: null,
				isCurrent: null
			}
		}
	},
	currentAlert: {
		message: null,
		show: false,
		variant: null
	},
	current_submission: null,
	route: '',
	currentSubmissionHistory: null,
	available_transitions: null,
	permissions: {
		dashboard: null,
		form: null,
		actions: null
	},
	tableRowConstructor: null,
	newTabs: [],
	form: null,
	initialData: {
		countryOptions: null,
		groupSubstances: null,
		substances: null,
		partyRatifications: null,
		blends: null,
		nonParties: null,
		display: {
			substances: null,
			blends: null,
			countries: null
		}
	},
	alertData: []
}

export default state
