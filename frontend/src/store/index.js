import Vue from 'vue'
import Vuex from 'vuex'
import form from '@/assets/form.js'
import tableRowConstructor from '@/mixins/tableRowConstructor'
import {
	getSubmissionHistory,
	callTransition,
	getSubstances,
	getSubmission,
	getCustomBlends,
	deleteSubmission,
	getSubmissions,
	getPeriods,
	getObligations,
	createSubmission,
	getParties
} from '@/api/api.js'

import dummyTransition from '@/assets/dummyTransition.js'

Vue.use(Vuex)

const intersect = (a, b) => {
	const setA = new Set(a)
	const setB = new Set(b)
	const intersection = new Set([...setA].filter(x => setB.has(x)))
	return Array.from(intersection)
}

const store = new Vuex.Store({
	// strict: true,
	state: {
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
		currentSubmissionHistory: null,
		available_transitions: null,
		permissions: {
			dashboard: null,
			form: null,
			actions: null
		},
		newTabs: [],
		form: null,
		initialData: {
			parties: null,
			countryOptions: null,
			groupSubstances: null,
			substances: null,
			blends: null,
			display: {
				substances: null,
				blends: null,
				countries: null
			}
		}
	},

	getters: {
		// ...
		getValidationForCurrentTab: (state) => (tab) => {
			if (['edited', false].includes(state.form.tabs[tab].status)) {
				return state.form.tabs[tab].form_fields.map(field => (field.validation.selected
					? { validation: field.validation.selected, substance: field.substance.selected, blend: field.blend ? field.blend.selected : null }
					: null))
			}
		},

		getDuplicateSubmission: (state) => (data) => state.dashboard.submissions.filter(
			(sub) => sub.obligation === data.obligation
                        && sub.party === data.party
                        && sub.reporting_period === data.reporting_period
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

		allowedChanges: (state) => {
			return !state.current_submission.data_changes_allowed
		}
	},

	actions: {

		addSubmission(context, data) {
			return new Promise((resolve, reject) => {
				const duplicate = context.getters.getDuplicateSubmission(data)
				if (duplicate.length) {
					context.dispatch('setAlert', { message: 'Another submission already exists in Data Entry stage.', variant: 'danger' })
					// TODO: should this be a thing ?
					// else if(!isReportingOpen) {
					//     context.dispatch('setAlert', { message: 'Reporting is not open for the selected period', variant: 'danger' })
					// }
				} else {
					createSubmission(data).then((response) => {
						context.dispatch('setAlert', { message: 'Submission Created', variant: 'success' })
						context.dispatch('getCurrentSubmissions').then(() => {
							resolve(response.data)
						})
					}).catch((error) => {
						context.dispatch('setAlert', { message: 'Failed to create submission', variant: 'danger' })
						reject(error.response)
					})
				}
			})
		},

		getCurrentSubmissions(context) {
			return new Promise((resolve) => {
				getSubmissions().then(response => {
					context.commit('setDashboardSubmissions', response.data)
					resolve()
				})
			})
		},

		async getDashboardParties(context) {
			let response
			try {
				response = await getParties()
			} catch (e) {
				console.log(e)
				return
			}

			const parties_temp = response.data
				.filter(country => country.id === country.parent_party)
				.map(country => ({ value: country.id, text: country.name }))
			context.commit('setDashboardParties', parties_temp)
		},

		getDashboardPeriods(context) {
			getPeriods().then(response => {
				let sortedPeriods = response.data
					.filter(a => a.is_reporting_allowed)
					.sort((a, b) => ((parseInt(b.end_date.split('-')[0]) - parseInt(a.end_date.split('-')[0])) === 0
						? (parseInt(b.start_date.split('-')[0]) - parseInt(a.start_date.split('-')[0]))
						: (parseInt(b.end_date.split('-')[0]) - parseInt(a.end_date.split('-')[0]))))
					.sort((a, b) => b.is_year - a.is_year)
				sortedPeriods = sortedPeriods.map((period) => {
					const start = period.start_date.split('-')[0]
					const end = period.end_date.split('-')[0]
					let periodDisplay = ''
					if (start === end) {
						if (period.name !== start) {
							periodDisplay += `(${start})`
						}
					} else {
						periodDisplay += `(${start} - ${end})`
					}

					return {
						value: period.id, text: `${period.name} ${periodDisplay}`, end_date: period.end_date, start_date: period.start_date, is_reporting_open: period.is_reporting_open
					}
				})

				context.commit('setDashboardPeriods', sortedPeriods)
			})
		},

		getDashboardObligations(context) {
			getObligations().then(response => {
				const obligations_temp = response.data.map(obligation => ({ value: obligation.id, text: obligation.name, form_type: obligation.form_type }))
				context.commit('setDashboardObligations', obligations_temp)
			})
		},

		resetAlert(context) {
			return new Promise((resolve) => {
				context.commit('setCurrentAlertMessage', null)
				context.commit('setCurrentAlertVisibility', false)
				context.commit('setCurrentAlertVariant', null)
				resolve()
			})
		},

		setAlert(context, data) {
			context.dispatch('resetAlert').then(() => {
				context.commit('setCurrentAlertMessage', data.message)
				context.commit('setCurrentAlertVisibility', true)
				context.commit('setCurrentAlertVariant', data.variant)
			})
		},

		prefillQuestionaire(context) {
			Object.keys(context.state.current_submission.article7questionnaire).forEach((element) => {
				context.commit('updateQuestionaireField', { value: context.state.current_submission.article7questionnaire[element], field: element })
			})
		},

		doSubmissionTransition(context, data) {
			callTransition(data.submission, data.transition).then(() => {
				context.dispatch('getSubmissionData', data.submission)
				context.dispatch('setAlert', { message: 'Submission state updated', variant: 'success' })
			}).catch(error => {
				context.dispatch('setAlert', { message: 'Unable to change the state of this submission', variant: 'danger' })
				console.log(error)
			})
		},

		removeSubmission(context, submissionUrl) {
			deleteSubmission(submissionUrl).then(() => {
				context.dispatch('getCurrentSubmissions')
				context.dispatch('setAlert', { message: 'Submission deleted', variant: 'success' })
			}).catch(() => {
				context.dispatch('getCurrentSubmissions')
				context.dispatch('setAlert', { message: 'Failed to delete submission', variant: 'danger' })
			})
		},

		getInitialData(context, data) {
			context.commit('getEmptyForm')
			return new Promise((resolve) => {
				context.dispatch('getSubmissionData', data).then(() => {
					context.dispatch('getCountries')
					context.dispatch('getSubstances')
					context.dispatch('getCustomBlends')
					resolve()
				})
			})
		},

		getSubmissionData(context, data) {
			return new Promise((resolve) => {
				getSubmission(data).then((response) => {
					context.commit('updateSubmissionData', response.data)
					context.commit('updateAvailableTransitions', response.data.available_transitions)
					if (context.state.current_submission.article7questionnaire) {
						context.dispatch('prefillQuestionaire')
					}
					context.dispatch('getCurrentSubmissionHistory', data)
					resolve()
				})
			})
		},

		getCurrentSubmissionHistory(context, data) {
			getSubmissionHistory(data).then((response) => {
				context.commit('setSubmissionHistory', response.data)
			}).catch((error) => {
				context.dispatch('setAlert', { message: error.response.data, variant: 'danger' })
			})
		},

		getParties(context) {
			getParties().then(response => {
				context.commit('updateParties', response.data)
			})
		},

		getCountries(context) {
			const countryDisplay = {}
			getParties().then(response => {
				const countryOptions = response.data.filter((p) => {
					countryDisplay[p.id] = p.name
					return p.id !== context.state.current_submission.party
				}).map((country) => ({ value: country.id, text: country.name }))
				context.commit('updateCountries', countryOptions)
				context.commit('updateCountriesDisplay', countryDisplay)
			})
		},

		getSubstances(context) {
			const tempSubstances = []
			const substancesDisplay = {}
			getSubstances().then((response) => {
				response.data.forEach(group => {
					group.substances.sort((a, b) => a.sort_order - b.sort_order)
					group.substances.forEach(substance => {
						tempSubstances.push({ value: substance.id, text: substance.name, group })
						substancesDisplay[substance.id] = substance.name
					})
				})

				context.commit('updateGroupSubstances', response.data)
				context.commit('updateSubstances', tempSubstances)
				context.commit('updateSubstancesDisplay', substancesDisplay)
			})
		},

		getCustomBlends(context) {
			const blendsDisplay = {}
			getCustomBlends().then((response) => {
				response.data.forEach(blend => {
					blend.components.sort((component1, component2) => component2.percentage - component1.percentage)
					blendsDisplay[blend.id] = { name: blend.blend_id, components: blend.components }
				})
				context.commit('updateBlends', response.data)
				context.commit('updateBlendsDisplay', blendsDisplay)
			})
		},

		createSubstance(context, data) {
			const substancesHere = data.substanceList && data.substanceList.some((el) => el !== null)
			const blendsHere = data.blendList && data.blendList.some((el) => el !== null)
			if (substancesHere) {
				data.substanceList.forEach(substance => {
					let ordering_id = 0
					if (!data.prefill) {
						context.commit('incrementOrderingId', { tabName: data.currentSectionName });
						({ ordering_id } = context.state.form.tabs[data.currentSectionName])
					}

					// section, substance, group, country, blend, prefillData, ordering_id
					const inner_fields = tableRowConstructor.getInnerFields({
						section: data.currentSectionName,
						substance,
						group: data.groupName,
						country: data.country,
						blend: null,
						prefillData: data.prefillData,
						ordering_id
					})
					context.commit('addSubstance', { sectionName: data.currentSectionName, row: inner_fields })
				})
			} else if (blendsHere) {
				data.blendList.forEach(blend => {
					let ordering_id = 0
					if (!data.prefill) {
						context.commit('incrementOrderingId', { tabName: data.currentSectionName });
						({ ordering_id } = context.state.form.tabs[data.currentSectionName].ordering_id)
					}
					const inner_fields = tableRowConstructor.getInnerFields({
						section: data.currentSectionName,
						substance: null,
						group: data.groupName,
						country: data.country,
						blend,
						prefillData: data.prefillData,
						ordering_id
					})
					context.commit('addSubstance', { sectionName: data.currentSectionName, row: inner_fields })
				})
			}
		},

		prefillEmissionsRow(context, data) {
			const row = {
				id: {
					selected: null
				},
				ordering_id: {
					selected: 0
				},
				facility_name: {
					type: 'text',
					selected: ''
				},
				quantity_generated: {
					type: 'number',
					selected: ''
				},
				quantity_feedstock: {
					type: 'number',
					selected: ''
				},
				quantity_destroyed: {
					type: 'number',
					selected: ''
				},
				quantity_emitted: {
					type: 'number',
					selected: ''
				},
				remarks_party: {
					type: 'textarea',
					selected: ''
				},
				remarks_os: {
					type: 'textarea',
					selected: ''
				},
				get validation() {
					const errors = []
					if (!this.facility_name.selected) {
						errors.push('eroare1')
					}

					const returnObj = {
						type: 'nonInput',
						selected: errors
					}

					return returnObj
				}
			}
			if (data) {
				Object.keys(data).forEach((element) => {
					row[element].selected = data[element]
				})
			}
			context.commit('addEmissionsRow', row)
		},

		removeDataFromTab(context, data) {
			return new Promise((resolve) => {
				context.commit('resetTab', data)
				resolve()
			})
		},

		uploadFormAttachments({ commit, state }, uploadedFiles) {
			// upload to the server
			// mocking server response
			const mockResponseAttachments = uploadedFiles.map(file => ({
				id: Math.floor(Math.random() * 100000),
				name: file.name,
				url: 'https://www.google.com',
				size: `${file.size} bytes`,
				dateUploaded: new Date(),
				description: `DESCRIPTION ${file.name} ${file.name} ${file.name} ${file.name} ${file.name} ${file.name} ${file.name} ${file.name} ${file.name} ${file.name} ${file.name}`
			}))
			commit('setFormAttachments', [...state.form.tabs.attachments, ...mockResponseAttachments])
		},

		saveFormAttachments({ state }) {
			alert('attachments saved')
			console.log(state.form.tabs.attachments)
		}
	},

	mutations: {
		// data - {value:value, fieldInfo:{index:tab_info.form_fields.indexOf(row),tabName: tabName, field:order}}
		updateFormField(state, data) {
			console.log(data.value)
			data.fieldInfo.index === data.fieldInfo.field
				? state.form.tabs[data.fieldInfo.tabName].form_fields[data.fieldInfo.index].selected = data.value
				: state.form.tabs[data.fieldInfo.tabName].form_fields[data.fieldInfo.index][data.fieldInfo.field].selected = data.value
		},

		setSubmissionHistory(state, data) {
			state.currentSubmissionHistory = data
		},

		getEmptyForm(state) {
			state.form = JSON.parse(JSON.stringify(form))
		},

		incrementOrderingId(state, data) {
			state.form.tabs[data.tabName].ordering_id += 1
		},

		setTabOrderingId(state, data) {
			state.form.tabs[data.tabName].ordering_id = data.ordering_id
		},

		// dashboard

		setDashboardParties(state, data) {
			state.dashboard.parties = data
		},
		setDashboardObligations(state, data) {
			state.dashboard.obligations = data
		},
		setDashboardPeriods(state, data) {
			state.dashboard.periods = data
		},
		setDashboardSubmissions(state, data) {
			state.dashboard.submissions = data
		},

		// alerts

		setCurrentAlertMessage(state, message) {
			state.currentAlert.message = message
		},

		setCurrentAlertVisibility(state, showState) {
			state.currentAlert.show = showState
		},

		setCurrentAlertVariant(state, variant) {
			state.currentAlert.variant = variant
		},

		// initial data

		updateAvailableTransitions(state, data) {
			state.available_transitions = data
		},

		updateSubmissionData(state, data) {
			state.current_submission = data
		},

		updateParties(state, data) {
			state.initialData.parties = data
		},

		updateCountries(state, data) {
			state.initialData.countryOptions = data
		},

		updateCountriesDisplay(state, data) {
			state.initialData.display.countries = data
		},

		updateGroupSubstances(state, data) {
			state.initialData.groupSubstances = data
		},

		updateSubstances(state, data) {
			state.initialData.substances = data
		},

		updateSubstancesDisplay(state, data) {
			state.initialData.display.substances = data
		},

		updateBlends(state, data) {
			state.initialData.blends = data
		},

		updateBlendsDisplay(state, data) {
			state.initialData.display.blends = data
		},

		setBlendComponentRowVariant(state, data) {
			data.component._rowVariant = data.value
		},

		// questionaire
		updateQuestionaireField(state, data) {
			const currentField = state.form.tabs.questionaire_questions.form_fields[data.field]
			currentField && (currentField.selected = data.value)
		},

		// addsubstance
		addSubstance(state, data) {
			state.form.tabs[data.sectionName].form_fields.push(data.row)
		},

		addEmissionsRow(state, data) {
			state.form.tabs.has_emissions.form_fields.push(data)
		},

		addCreateBlendToBlendList(state, data) {
			state.initialData.blends.push(data)
		},

		setTabStatus(state, data) {
			state.form.tabs[data.tab].status = data.value
		},

		// permissions
		updateDashboardPermissions(state, permission) {
			state.permissions.dashboard = permission
		},
	
		updateActionsPermissions(state, permission) {
			state.permissions.actions = permission
		},

		// form state
		updateNewTabs(state, tab) {
			state.newTabs.push(tab)
		},

		tabHasBeenSaved(state, tab) {
			state.newTabs = state.newTabs.filter(currentTab => currentTab !== tab)
		},

		// removal

		resetTab(state, tab) {
			state.form.tabs[tab].form_fields = []
		},

		removeField(state, data) {
			state.form.tabs[data.tab].form_fields.splice(data.index, 1)
		},

		setFormAttachments(state, attachments) {
			state.form.tabs.attachments = attachments
		},

		updateFormAttachment(state, attachment) {
			const updatedAttachments = []
			state.form.tabs.attachments.forEach(attach => {
				attach.id === attachment.id ? updatedAttachments.push(attachment) : updatedAttachments.push(attach)
			})
			state.form.tabs.attachments = updatedAttachments
		},
		deleteFormAttachment(state, attachment) {
			state.form.tabs.attachments = state.form.tabs.attachments.filter(attach => attach.id !== attachment.id)
		}
	}
})

export default store
