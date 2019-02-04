import {
	getSubmissionHistory,
	callTransition,
	getSubstances,
	getCustomBlends,
	getSubmissions,
	getSubmission,
	getSubmissionFiles,
	deleteSubmission,
	deleteSubmissionFile,
	updateSubmissionFiles,
	getPeriods,
	getObligations,
	createSubmission,
	getParties,
	getNonParties,
	getPartyRatifications,
	getCurrentUser,
	updateCurrentUser,
	uploadFile
} from '@/components/common/services/api'

import {
	getLevel2PropertyValue
} from '@/components/common/services/utilsService.js'

import { getLabels } from '@/components/art7/dataDefinitions/labels'

const actions = {
	addSubmission(context, { submission, $gettext }) {
		return new Promise((resolve, reject) => {
			const duplicate = context.getters.getDuplicateSubmission(submission)
			if (duplicate.length) {
				context.dispatch('setAlert', {
					$gettext,
					message: { __all__: [$gettext('Another submission already exists in Data Entry stage.')] },
					variant: 'danger'
				})
				// TODO: should this be a thing ?
				// else if(!isReportingOpen) {
				//     context.dispatch('setAlert', { message: 'Reporting is not open for the selected period', variant: 'danger' })
				// }
			} else {
				createSubmission(submission).then((response) => {
					context.dispatch('setAlert', {
						$gettext,
						message: { __all__: [$gettext('Submission created')] },
						variant: 'success'
					})
					context.dispatch('getCurrentSubmissions').then(() => {
						resolve(response.data)
					})
				}).catch((error) => {
					context.dispatch('setAlert', {
						$gettext,
						message: { __all__: [$gettext('Failed to create submission')] },
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

	async getMyCurrentUser({ commit, dispatch }) {
		let response
		try {
			response = await getCurrentUser()
			commit('setCurrentUser', response.data)
			// TODO: WHY IS IT AN ARRAY ?
			commit('setCurrentUserPartyInDashboard', response.data[0].party)
			dispatch('getCurrentSubmissions')
		} catch (e) {
			console.log('getMyCurrentUser', e)
		}
	},

	async updateCurrentUser({ dispatch }, user) {
		try {
			await updateCurrentUser(user)
			dispatch('getMyCurrentUser')
		} catch (e) {
			console.log('updateCurrentUser', e)
		}
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
				},
				perPage: null,
				currentPage: null
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
			.map(country => ({ value: country.id, text: country.name, iso: country.abbr }))
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
			const labelValue = getLevel2PropertyValue(getLabels(data.$gettext), key)
			const message = typeof (data.message[key]) !== 'string' ? data.message[key].join('<br>') : data.message[key]
			const displayMessage = `${labelValue ? `${labelValue}: ` : ''}${message}`
			context.commit('addAlertData', {
				displayMessage,
				variant: data.variant
			})
		})
	},

	doSubmissionTransition(context, { source, submission, transition, $gettext }) {
		callTransition(submission, transition).then(() => {
			if (source === 'dashboard') {
				context.dispatch('getCurrentSubmissions')
			} else {
				context.dispatch('getSubmissionData', { submission, $gettext })
			}
			context.dispatch('setAlert', {
				$gettext,
				message: { __all__: [$gettext('Submission state updated')] },
				variant: 'success'
			})
		}).catch(error => {
			context.dispatch('setAlert', {
				$gettext,
				message: { __all__: [$gettext('Unable to change the state of this submission')] },
				variant: 'danger'
			})
			console.log(error)
		})
	},

	removeSubmission(context, { submissionUrl, $gettext }) {
		deleteSubmission(submissionUrl).then(() => {
			context.dispatch('getCurrentSubmissions')
			context.dispatch('setAlert', {
				$gettext,
				message: { __all__: [$gettext('Submission deleted')] },
				variant: 'success'
			})
		}).catch(() => {
			context.dispatch('getCurrentSubmissions')
			context.dispatch('setAlert', {
				$gettext,
				message: { __all__: [$gettext('Failed to delete submission')] },
				variant: 'danger'
			})
		})
	},

	getInitialData(context, { submission, formName, $gettext }) {
		context.commit('setForm', { formName, $gettext })
		return new Promise((resolve) => {
			context.dispatch('getSubmissionData', { submission, $gettext }).then(() => {
				context.dispatch('getCurrentUserForm')
				context.dispatch('getCountries')
				context.dispatch('getSubstances')
				// Filter custom blends by the submission's party, because the API will
				// by default show all custom blends for secretariat users.
				// This way, even secretariat users will only see the correct available
				// custom blends.
				context.dispatch('getCustomBlends', { party: context.state.current_submission.party })
				context.dispatch('getNonParties')
				resolve()
			})
		})
	},

	getSubmissionData(context, { submission, $gettext }) {
		return new Promise((resolve) => {
			getSubmission(submission).then((response) => {
				context.commit('updateSubmissionData', response.data)
				context.commit('setFlagsPermissions', response.data.changeable_flags)
				context.commit('updateAvailableTransitions', response.data.available_transitions)
				context.dispatch('getCurrentSubmissionHistory', { submission, $gettext })
				context.commit('setFormPermissions', {
					can_change_remarks_party: response.data.can_change_remarks_party,
					can_change_remarks_secretariat: response.data.can_change_remarks_secretariat,
					can_change_reporting_channel: response.data.can_change_reporting_channel,
					can_upload_files: response.data.can_upload_files,
					can_edit_data: response.data.can_edit_data
				})
				resolve()
			})
		})
	},

	getCurrentSubmissionHistory(context, { submission, $gettext }) {
		getSubmissionHistory(submission).then((response) => {
			context.commit('setSubmissionHistory', response.data)
		}).catch((error) => {
			context.dispatch('setAlert', {
				$gettext,
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
			}).map((country) => ({ value: country.id, text: country.name, iso: country.abbr }))
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
					tempSubstances.push({
						value: substance.id,
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

	getCustomBlends(context, { party }) {
		const blendsDisplay = {}
		getCustomBlends(party).then((response) => {
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
				const inner_fields = context.state.tableRowConstructor.substanceRows({
					$gettext: data.$gettext,
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
				const inner_fields = context.state.tableRowConstructor.substanceRows({
					$gettext: data.$gettext,
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

	createRow(context, { currentSectionName, prefillData, $gettext }) {
		let ordering_id = 0
		if (!prefillData) {
			context.commit('incrementOrderingId', { tabName: currentSectionName });
			({ ordering_id } = context.state.form.tabs[currentSectionName])
		}

		const row = context.state.tableRowConstructor.nonSubstanceRows({
			$gettext,
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
	async uploadFiles(context, { files, onProgressCallback }) {
		for (let i = 0; i < files.length; i += 1) {
			const file = files[i]
			const response = await uploadFile(file, context.state.current_submission.id, onProgressCallback)
			file.tus_url = response.url
			file.percentage = 100
		}
	},
	async getSubmissionFiles(context) {
		const response = await getSubmissionFiles(context.state.current_submission.id)
		return response.data
	},
	async deleteTabFile({ state, commit }, { tabName, file }) {
		console.log(file)
		if (file.tus_id) {
			await deleteSubmissionFile({ file, submissionId: state.current_submission.id })
		}

		commit('deleteTabFile', { tabName, file })
	},
	updateLocalFilesFromServerFilesResponse({ commit }, { tabName, filesLocal, filesOnServer }) {
		filesOnServer.forEach(file => {
			const fileJustUploaded = filesLocal.find(x => {
				if (x.tus_id) {
					return x.tus_id === file.tus_id
				}
				return x.tus_url && x.tus_url.endsWith(file.tus_id)
			})
			if (fileJustUploaded) {
				commit('deleteTabFile', {
					tabName,
					file: fileJustUploaded
				})
				fileJustUploaded.upload_successful = file.upload_successful
				fileJustUploaded.file_url = file.file_url
				fileJustUploaded.updated = file.updated
				fileJustUploaded.tus_id = file.tus_id
				commit('addTabFile', {
					tabName,
					file: fileJustUploaded
				})
			}
		})
	},
	async setJustUploadedFilesState({ dispatch }, { files, tabName }) {
		const filesOnServer = await dispatch('getSubmissionFiles')
		dispatch('updateLocalFilesFromServerFilesResponse', {
			tabName,
			filesOnServer,
			filesLocal: files
		})
	},
	async updateSubmissionFiles({ state, dispatch }, { files, tabName }) {
		const response = await updateSubmissionFiles(state.current_submission.id, files.map(file => ({
			id: file.id,
			name: file.name,
			description: file.description
		})))
		dispatch('updateLocalFilesFromServerFilesResponse', {
			tabName,
			filesOnServer: response.data,
			filesLocal: files
		})
	}
}

export default actions
