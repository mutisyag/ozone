import 'toastedjs/src/sass/toast.scss'
import Toasted from 'toastedjs'

import art7Form from '@/components/art7/dataDefinitions/form'
import art7TableRowConstructor from '@/components/art7/services/tableRowConstructorService'
import letterForm from '@/components/letter/dataDefinitions/form'
import letterTableRowConstructor from '@/components/letter/services/tableRowConstructorService'
import hatForm from '@/components/hat/dataDefinitions/form'
import hatTableRowConstructor from '@/components/hat/services/tableRowConstructorService'

const options = {
	position: 'bottom-left',
	duration: 10000,
	theme: 'bulma'
}
const toasted = new Toasted(options)

const mutations = {
	updateBreadcrumbs(state, data) {
		state.route = data.join(' / ')
	},

	addComment(state, { data, tab, field }) {
		// If there is no field specified, it means that the data comes from server for prefill
		console.log('comments', data, tab, field)
		if (!field) {
			const [commentsData] = data
			Object.keys(state.form.tabs[tab].comments).forEach(comment => {
				state.form.tabs[tab].comments[comment].selected = commentsData[comment]
			})
		} else {
			state.form.tabs[tab].comments[field].selected = data
		}
	},

	updateFormField(state, data) {
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
		state.dashboard.submissions = data.results
		state.dashboard.table.totalRows = data.count
	},
	setCurrentUserPartyInDashboard(state, data) {
		state.dashboard.table.filters.party = data
	},
	setDashboardMySubmissions(state, data) {
		state.dashboard.mySubmissions = data
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

	setCurrentUser(state, data) {
		[state.currentUser] = data
	},

	updateSubmissionData(state, data) {
		state.current_submission = data
	},

	updatePartyRatifications(state, data) {
		const htmlFormatter = (ratification) => (ratification ? `${ratification.ratification_date} <br/> ${ratification.ratification_type}` : 'Pending')

		data = data.map(party => {
			party.vienna_convention = htmlFormatter(party.ratifications.find(ratification => ratification.treaty && ratification.treaty.treaty_id === 'VC'))
			party.montreal_protocol = htmlFormatter(party.ratifications.find(ratification => ratification.treaty && ratification.treaty.treaty_id === 'MP'))
			party.london_amendment = htmlFormatter(party.ratifications.find(ratification => ratification.treaty && ratification.treaty.treaty_id === 'LA'))
			party.copenhagen_amendment = htmlFormatter(party.ratifications.find(ratification => ratification.treaty && ratification.treaty.treaty_id === 'CA'))
			party.montreal_amendment = htmlFormatter(party.ratifications.find(ratification => ratification.treaty && ratification.treaty.treaty_id === 'MA'))
			party.beijing_amendment = htmlFormatter(party.ratifications.find(ratification => ratification.treaty && ratification.treaty.treaty_id === 'BA'))
			party.kigali_amendment = htmlFormatter(party.ratifications.find(ratification => ratification.treaty && ratification.treaty.treaty_id === 'KA'))
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
		Object.keys(state.form.tabs[tabName].form_fields).forEach(field => {
			if (data[field] !== undefined) {
				state.form.tabs[tabName].form_fields[field].selected = data[field]
			}
		})
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

	setFlagsPermissions(state, data) {
		// some forms either might not have flags or the flags will be implemented on a latter date
		// the "state.form.tabs.flags &&" verification prvents hard failure for those forms
		state.form.tabs.flags && Object.keys(state.form.tabs.flags.form_fields).forEach(key => {
			if (data.includes(key)) state.form.tabs.flags.form_fields[key].disabled = false
		})
	},

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

	addTabAttachments(state, { tabName, attachments }) {
		if (!attachments) {
			return
		}
		attachments.forEach(attachment => {
			state.form.tabs[tabName].form_fields.attachments.push(attachment)
		})
	},
	updateTabAttachment(state, { tabName, attachment }) {
		const updatedAttachments = []
		state.form.tabs[tabName].form_fields.attachments.forEach(attachOld => {
			attachOld === attachment ? updatedAttachments.push(attachment) : updatedAttachments.push(attachOld)
		})
		state.form.tabs[tabName].form_fields.attachments = updatedAttachments
	},
	deleteTabAttachment(state, { tabName, attachment }) {
		state.form.tabs[tabName].form_fields.attachments = state.form.tabs[tabName].form_fields.attachments.filter(attachOld => attachOld !== attachment)
	},
	deleteAllTabAttachments(state, { tabName }) {
		state.form.tabs[tabName].form_fields.attachments = []
	}
}

export default mutations
