<template>
    <b-btn
		:disabled="isFilesUploadInProgress"
		@click="validation"
		id="save-button"
		ref="save_button"
		variant="primary">
			<span v-translate>Save and continue</span>
    </b-btn>
</template>

<script>

import { post, update } from '@/components/common/services/api'
import { isObject } from '@/components/common/services/utilsService'
import { dateFormatToYYYYMMDD } from '@/components/common/services/languageService'
import FilesMixin from './FilesMixin'

export default {
	mixins: [FilesMixin],
	props: {
		submission: String
	},

	data() {
		return {
			invalidTabs: [],
			tabsToSave: []
		}
	},

	computed: {
		form() {
			return this.$store.state.form
		},
		newTabs() {
			return this.$store.state.newTabs
		},
		is_secretariat() {
			return this.$store.state.currentUser.is_secretariat
		}
	},

	methods: {
		validation() {
			this.invalidTabs = []
			const tabsToValidate = Object.values(this.form.tabs).filter(tab => tab.validate).map(tab => tab.name)
			for (const tab of tabsToValidate) {
				if (Array.isArray(this.form.tabs[tab].form_fields)) {
					for (const field of this.form.tabs[tab].form_fields) {
						if (field.validation.selected.length) {
							this.invalidTabs.push(this.form.tabs[tab].name)
							this.$store.commit('setTabStatus', { tab, value: false })
							break
						}
					}
				} else {
					console.log(this.form.tabs[tab].form_fields.validation.selected.length)
					if (this.form.tabs[tab].form_fields.validation && this.form.tabs[tab].form_fields.validation.selected.length) {
						this.invalidTabs.push(this.form.tabs[tab].name)
						this.$store.commit('setTabStatus', { tab, value: false })
					}
				}
			}
			if (this.invalidTabs.length) {
				this.$store.dispatch('setAlert', {
					$gettext: this.$gettext,
					message: { __all__: [`${this.$gettextInterpolate('Save failed  because of validation problems. Please check the %{invalidTabs}', { invalidTabs: this.invalidTabs.join(', ') })}  <i data-v-676ba8cf="" class="fa fa-times-circle fa-lg ml-2 mr-2"></i> form`] },
					variant: 'danger'
				})
			} else {
				this.prepareCommentsForSave()
				this.prepareDataForSave()
			}
		},

		prepareCommentsForSave() {
			if (!this.form.formDetails.comments_default_properties) return
			const commentsObj = JSON.parse(JSON.stringify(this.form.formDetails.comments_default_properties))
			Object.keys(this.form.tabs).forEach(tab => {
				this.form.tabs[tab].comments && Object.keys(this.form.tabs[tab].comments).forEach(comment_field => {
					commentsObj[comment_field] = this.form.tabs[tab].comments[comment_field].selected
				})
			})
			const url = this.$store.state.current_submission[this.form.formDetails.comments_endpoint_url]
			this.saveComments(commentsObj, url)
		},

		async saveComments(data, url) {
			try {
				await update(url, data)
			} catch (error) {
				console.log(error)
				this.$store.dispatch('setAlert', {
					$gettext: this.$gettext,
					message: error,
					variant: 'danger'
				})
			}
		},

		async submitData(tab, url) {
			if (tab.name === 'sub_info' && !this.$store.getters.can_edit_data) {
				return
			}
			if (tab.skipSave) {
				return
			}
			if (tab.status !== null) {
				this.$store.commit('setTabStatus', { tab: tab.name, value: 'saving' })
			}
			let current_tab_data

			if (Array.isArray(tab.form_fields)) {
				current_tab_data = []
				tab.form_fields.forEach(form_field => {
					const save_obj = JSON.parse(JSON.stringify(tab.default_properties))
					for (const row in form_field) {
						// special case for raf imports
						if (!Array.isArray(form_field[row])) {
							save_obj[row] = form_field[row].selected
						} else {
							save_obj[row] = form_field[row]
						}

						if (form_field[row].type === 'date') {
							save_obj[row] = dateFormatToYYYYMMDD(save_obj[row], this.$language.current)
						}
					}
					current_tab_data.push(save_obj)
				})
			}

			if (isObject(tab.form_fields)) {
				const save_obj = JSON.parse(JSON.stringify(tab.default_properties))
				current_tab_data = {}
				Object.keys(save_obj).forEach(key => {
					if (key === 'submitted_at' && !this.is_secretariat) {
						return
					}
					current_tab_data[key] = tab.form_fields[key].selected
					if (tab.form_fields[key].type === 'date') {
						current_tab_data[key] = dateFormatToYYYYMMDD(current_tab_data[key], this.$language.current)
					}
				})
			}

			try {
				if (this.newTabs.includes(tab.name) && tab.name !== 'files') {
					await post(url, current_tab_data)
					this.$store.commit('setTabStatus', { tab: tab.name, value: true })

					if (isObject(tab.form_fields)) {
						this.$store.commit('tabHasBeenSaved', tab.name)
					}

					if (Array.isArray(tab.form_fields)) {
						if (tab.form_fields.length) {
							this.$store.commit('tabHasBeenSaved', tab.name)
						} else {
							this.$store.commit('updateNewTabs', tab.name)
						}
					}
				} else {
					if (tab.name === 'files') {
						await this.uploadFiles()

						current_tab_data = this.getFilesWithUpdatedDescription()
							.map(file => ({
								id: file.id,
								name: file.name,
								description: file.description
							}))
					}

					await update(url, current_tab_data)

					if (tab.name === 'files') {
						await this.getSubmissionFiles()
					}
					if (tab.status !== null) {
						this.$store.commit('setTabStatus', { tab: tab.name, value: true })
					}

					if (Array.isArray(tab.form_fields)) {
						if (!tab.form_fields.length) {
							this.$store.commit('updateNewTabs', tab.name)
						}
					}
				}
				if (tab.name === 'sub_info') {
					this.$store.dispatch('getNewTransitions')
				}
			} catch (error) {
				this.$store.commit('setTabStatus', { tab: tab.name, value: false })
				console.log(error)
				this.$store.dispatch('setAlert', {
					$gettext: this.$gettext,
					message: { __all__: [this.$gettext('Save failed')] },
					variant: 'danger' })
			}
			this.tabsToSave = this.tabsToSave.filter(t => t !== tab.name)
			if (this.tabsToSave.length === 0 && this.$store.state.actionToDispatch) {
				this.$store.dispatch('saveCallback', { actionToDispatch: this.$store.state.actionToDispatch, data: this.$store.state.dataForAction })
				this.$store.commit('setActionToDispatch', null)
				this.$store.commit('setDataForAction', null)
			}
		}
	}
}
</script>
