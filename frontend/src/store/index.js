import Vue from 'vue'
import Vuex from 'vuex'
import art7Form from '@/components/art7/dataDefinitions/form'
import art7TableRowConstructor from '@/components/art7/services/tableRowConstructorService'
import letterForm from '@/components/letter/dataDefinitions/form'
import letterTableRowConstructor from '@/components/letter/services/tableRowConstructorService'
import hatForm from '@/components/hat/dataDefinitions/form'
import hatTableRowConstructor from '@/components/hat/services/tableRowConstructorService'

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
	getParties,
	getNonParties,
	getPartyRatifications
} from '@/components/common/services/api'
import 'toastedjs/src/sass/toast.scss'
import {
	getLevel2PropertyValue
} from '@/components/common/services/utilsService.js'
import labels from '@/components/art7/dataDefinitions/labels'
import Toasted from 'toastedjs'

const options = {
	position: 'bottom-left',
	duration: 10000,
	theme: 'bulma'
}
const toasted = new Toasted(options)

Vue.use(Vuex)

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

		allowedChanges: (state) => (state.current_submission ? !state.current_submission.data_changes_allowed : false)
	},

	actions: {

		addSubmission(context, data) {
			return new Promise((resolve, reject) => {
				const duplicate = context.getters.getDuplicateSubmission(data)
				if (duplicate.length) {
					context.dispatch('setAlert', {
						message: { __all__: ['Another submission already exists in Data Entry stage.'] },
						variant: 'danger'
					})
					// TODO: should this be a thing ?
					// else if(!isReportingOpen) {
					//     context.dispatch('setAlert', { message: 'Reporting is not open for the selected period', variant: 'danger' })
					// }
				} else {
					createSubmission(data).then((response) => {
						context.dispatch('setAlert', {
							message: { __all__: ['Submission Created'] },
							variant: 'success'
						})
						context.dispatch('getCurrentSubmissions').then(() => {
							resolve(response.data)
						})
					}).catch((error) => {
						context.dispatch('setAlert', {
							message: { __all__: ['Failed to create submission'] },
							variant: 'danger'
						})
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

		setAlert(context, data) {
			Object.keys(data.message).forEach(key => {
				const labelValue = getLevel2PropertyValue(labels, key)
				const displayMessage = `${labelValue ? `${labelValue}: ` : ''}${data.message[key].join('<br>')}`
				context.commit('addAlertData', {
					displayMessage,
					variant: data.variant
				})
			})
		},

		doSubmissionTransition(context, data) {
			callTransition(data.submission, data.transition).then(() => {
				if (data.source === 'dashboard') {
					context.dispatch('getCurrentSubmissions')
				} else {
					context.dispatch('getSubmissionData', data.submission)
				}
				context.dispatch('setAlert', {
					message: { __all__: ['Submission state updated'] },
					variant: 'success'
				})
			}).catch(error => {
				context.dispatch('setAlert', {
					message: { __all__: ['Unable to change the state of this submission'] },
					variant: 'danger'
				})
				console.log(error)
			})
		},

		removeSubmission(context, submissionUrl) {
			deleteSubmission(submissionUrl).then(() => {
				context.dispatch('getCurrentSubmissions')
				context.dispatch('setAlert', {
					message: { __all__: ['Submission deleted'] },
					variant: 'success'
				})
			}).catch(() => {
				context.dispatch('getCurrentSubmissions')
				context.dispatch('setAlert', {
					message: { __all__: ['Failed to delete submission'] },
					variant: 'danger'
				})
			})
		},

		getInitialData(context, { submission, formName }) {
			context.commit('setForm', formName)
			return new Promise((resolve) => {
				context.dispatch('getSubmissionData', submission).then(() => {
					context.dispatch('getCountries')
					context.dispatch('getSubstances')
					context.dispatch('getCustomBlends')
					context.dispatch('getNonParties')
					resolve()
				})
			})
		},

		getSubmissionData(context, data) {
			return new Promise((resolve) => {
				getSubmission(data).then((response) => {
					context.commit('updateSubmissionData', response.data)
					context.commit('updateAvailableTransitions', response.data.available_transitions)
					context.dispatch('getCurrentSubmissionHistory', data)
					resolve()
				})
			})
		},

		getCurrentSubmissionHistory(context, data) {
			getSubmissionHistory(data).then((response) => {
				context.commit('setSubmissionHistory', response.data)
			}).catch((error) => {
				context.dispatch('setAlert', {
					message: { ...error.response.data },
					variant: 'danger'
				})
			})
		},

		getPartyRatifications(context) {
			getPartyRatifications().then(response => {
				context.commit('updatePartyRatifications', response.data)
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
						tempSubstances.push({ value: substance.id, text: substance.name, group, is_qps: substance.is_qps })
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
					blendsDisplay[blend.id] = { name: blend.blend_id, components: blend.components, is_qps: blend.is_qps }
				})
				context.commit('updateBlends', response.data)
				context.commit('updateBlendsDisplay', blendsDisplay)
			})
		},

		getNonParties(context) {
			getNonParties().then((response) => {
				context.commit('updateNonParties', response.data)
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
					const inner_fields = context.state.tableRowConstructor.getInnerFields({
						section: data.currentSectionName,
						substance,
						group: data.groupName,
						country: data.country,
						blend: null,
						prefillData: data.prefillData,
						ordering_id
					})
					context.commit('addRow', { sectionName: data.currentSectionName, row: inner_fields })
				})
			} else if (blendsHere) {
				data.blendList.forEach(blend => {
					let ordering_id = 0
					if (!data.prefill) {
						context.commit('incrementOrderingId', { tabName: data.currentSectionName });
						({ ordering_id } = context.state.form.tabs[data.currentSectionName].ordering_id)
					}
					const inner_fields = context.state.tableRowConstructor.getInnerFields({
						section: data.currentSectionName,
						substance: null,
						group: data.groupName,
						country: data.country,
						blend,
						prefillData: data.prefillData,
						ordering_id
					})
					context.commit('addRow', { sectionName: data.currentSectionName, row: inner_fields })
				})
			}
		},

		createRow(context, { currentSectionName, prefillData }) {
			let ordering_id = 0
			if (!prefillData) {
				context.commit('incrementOrderingId', { tabName: currentSectionName });
				({ ordering_id } = context.state.form.tabs[currentSectionName])
			}

			const row = context.state.tableRowConstructor.getSimpleTabFields({
				currentSectionName,
				prefillData,
				ordering_id
			})
			context.commit('addRow', { sectionName: currentSectionName, row })
		},

		removeDataFromTab(context, data) {
			return new Promise((resolve) => {
				context.commit('resetTab', data)
				resolve()
			})
		},
		uploadFormAttachments(context, uploadedFiles) {
			// upload to the server
			// mocking server response
			const mockResponseAttachments = uploadedFiles.map(file => ({
				id: Math.floor(Math.random() * 100000),
				name: file.name,
				url: 'https://www.google.com',
				size: `${file.size} bytes`,
				dateUploaded: new Date(),
				description: `DESCRIPTION ${file.name}`
			}))
			return mockResponseAttachments
		}
	},

	mutations: {
		updateFormField(state, data) {
			console.log(data.value)
			data.fieldInfo.index === data.fieldInfo.field
				? state.form.tabs[data.fieldInfo.tabName].form_fields[data.fieldInfo.index].selected = data.value
				: state.form.tabs[data.fieldInfo.tabName].form_fields[data.fieldInfo.index][data.fieldInfo.field].selected = data.value
		},

		setSubmissionHistory(state, data) {
			state.currentSubmissionHistory = data
		},

		setForm(state, data) {
			let currentFormStructure = null
			let tableRowConstructor = null
			console.log('setForm', data)
			switch (data) {
			case 'art7':
				currentFormStructure = art7Form
				tableRowConstructor = art7TableRowConstructor
				break
			case 'hat':
				currentFormStructure = hatForm
				tableRowConstructor = hatTableRowConstructor
				break
			case 'letter':
				currentFormStructure = letterForm
				tableRowConstructor = letterTableRowConstructor
				break
			default:
				break
			}
			state.form = JSON.parse(JSON.stringify(currentFormStructure))
			state.tableRowConstructor = tableRowConstructor
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

		updatePartyRatifications(state, data) {
			data = data.map(party => {
				party.vienna_convention = party.ratifications.find(ratification => ratification.treaty && ratification.treaty.treaty_id === 'VC')
				party.montreal_protocol = party.ratifications.find(ratification => ratification.treaty && ratification.treaty.treaty_id === 'MP')
				party.london_amendment = party.ratifications.find(ratification => ratification.treaty && ratification.treaty.treaty_id === 'LA')
				party.copenhagen_amendment = party.ratifications.find(ratification => ratification.treaty && ratification.treaty.treaty_id === 'CA')
				party.montreal_amendment = party.ratifications.find(ratification => ratification.treaty && ratification.treaty.treaty_id === 'MA')
				party.beijing_amendment = party.ratifications.find(ratification => ratification.treaty && ratification.treaty.treaty_id === 'BA')
				party.kigali_amendment = party.ratifications.find(ratification => ratification.treaty && ratification.treaty.treaty_id === 'KA')
				party.is_eu_member = party.flags.is_eu_member
				party.is_article5 = party.flags.is_article5
				party.is_high_ambient_temperature = party.flags.is_high_ambient_temperature
				return party
			})
			state.initialData.partyRatifications = data
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

		updateNonParties(state, data) {
			state.initialData.nonParties = data
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

		addAlertData(state, data) {
			const toastedOptions = {
				danger: 'error',
				success: 'success'
			}
			const now = new Date()
			state.alertData = state.alertData.filter(x => x.expires > now)
			const existingDisplayMessage = state.alertData.find(x => x.displayMessage === data.displayMessage)
			if (!existingDisplayMessage) {
				state.alertData.push({
					...data,
					expires: new Date((new Date()).getTime() + 5000)
				})
				toasted.show(data.displayMessage, { type: toastedOptions[data.variant] })
			}
		},

		// questionaire
		updateQuestionaireField(state, data) {
			const currentField = state.form.tabs.questionaire_questions.form_fields[data.field]
			currentField && (currentField.selected = data.value)
		},

		prefillTab(state, { tabName, data }) {
			console.log('prefilling tab', tabName, data)
			Object.keys(state.form.tabs[tabName].form_fields).forEach(field => { state.form.tabs[tabName].form_fields[field].selected = data[field] })
		},
		// addRow
		addRow(state, { sectionName, row }) {
			state.form.tabs[sectionName].form_fields.push(row)
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
			if (tab !== 'sub_info') state.newTabs = Array.from(new Set([...state.newTabs, ...[tab]]))
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

		setTabAttachments(state, { tabName, attachments }) {
			state.form.tabs[tabName].form_fields.attachments = attachments
		},
		addTabAttachment(state, { tabName, attachment }) {
			state.form.tabs[tabName].form_fields.attachments.push(attachment)
		},
		updateTabAttachment(state, { tabName, attachment }) {
			const updatedAttachments = []
			state.form.tabs[tabName].form_fields.attachments.forEach(attach => {
				attach.id === attachment.id ? updatedAttachments.push(attachment) : updatedAttachments.push(attach)
			})
			state.form.tabs[tabName].form_fields.attachments = updatedAttachments
		},
		deleteTabAttachment(state, { tabName, attachment }) {
			state.form.tabs[tabName].form_fields.attachments = state.form.tabs[tabName].form_fields.attachments.filter(attach => attach.id !== attachment.id)
		}
	}
})

export default store
