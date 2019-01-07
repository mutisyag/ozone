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
	getPartyRatifications,
	getCurrentUser
} from '@/components/common/services/api'

import {
	getLevel2PropertyValue
} from '@/components/common/services/utilsService.js'

import labels from '@/components/art7/dataDefinitions/labels'

const actions = {
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

	prefillComments(context, data) {
		Object.keys(context.state.form.tabs)
			.filter(tab => context.state.form.tabs[tab].comments)
			.forEach(tab => context.commit('addComment', { data, tab }))
	},

	getCurrentSubmissions(context) {
		return new Promise((resolve) => {
			getSubmissions(context.state.dashboard.table).then(response => {
				context.commit('setDashboardSubmissions', response.data)
				context.dispatch('getMyCurrentSubmissions')
				resolve()
			})
		})
	},

	getMyCurrentUser(context) {
		getCurrentUser().then(response => {
			context.commit('setCurrentUser', response.data)
			// TODO: WHY IS IT AN ARRAY ?
			context.commit('setCurrentUserPartyInDashboard', response.data[0].party)
			context.dispatch('getCurrentSubmissions')
		})
	},

	getCurrentUserForm(context) {
		getCurrentUser().then(response => {
			context.commit('setCurrentUser', response.data)
		})
	},

	getMyCurrentSubmissions(context) {
		return new Promise((resolve) => {
			getSubmissions({
				filters: {
					currentState: 'data_entry',
					party: context.state.currentUser.party
				},
				sorting: {
					sortDesc: true,
					sortBy: 'updated_at'
				}

			}).then(response => {
				context.commit('setDashboardMySubmissions', response.data)
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
			const message = typeof (data.message[key]) !== 'string' ? data.message[key].join('<br>') : data.message[key]
			const displayMessage = `${labelValue ? `${labelValue}: ` : ''}${message}`
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
				context.dispatch('getCurrentUserForm')
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
				context.commit('setFlagsPermissions', response.data.changeable_flags)
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
					tempSubstances.push({ value: substance.id,
						text: substance.name,
						group,
						is_qps: substance.is_qps,
						is_contained_in_polyols: substance.is_contained_in_polyols
					})
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
}

export default actions
