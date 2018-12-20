import Vue from 'vue'
import Vuex from 'vuex'
import getters from './getters'
import mutations from './mutations'
import actions from './actions'

Vue.use(Vuex)

const state = {
	dashboard: {
		submissions: null,
		periods: null,
		obligations: null,
		parties: null
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

const store = new Vuex.Store({
	state,
	getters,
	mutations,
	actions
})

export default store
