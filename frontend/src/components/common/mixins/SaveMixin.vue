<template>
    <b-btn
			@click="validation"
			id="save-button"
			variant="primary">
        <span v-translate>Save and continue</span>
    </b-btn>
</template>

<script>

import { post, update } from '@/components/common/services/api'
import { isObject } from '@/components/common/services/utilsService'
import FilesMixin from './FilesMixin'

export default {
	mixins: [FilesMixin],
	props: {
		submission: String
	},

	data() {
		return {
			invalidTabs: []
		}
	},

	computed: {
		form() {
			return this.$store.state.form
		},
		newTabs() {
			return this.$store.state.newTabs
		}
	},

	methods: {

		validation() {
			this.invalidTabs = []
			const tabsToValidate = Object.values(this.form.tabs).filter(tab => tab.validate).map(tab => tab.name)
			for (const tab of tabsToValidate) {
				for (const field of this.form.tabs[tab].form_fields) {
					if (field.validation.selected.length) {
						this.invalidTabs.push(this.form.tabs[tab].name)
						this.$store.commit('setTabStatus', { tab, value: false })
						break
					}
				}
			}
			if (this.invalidTabs.length) {
				this.$store.dispatch('setAlert', {
					$gettext: this.$gettext,
					message: { __all__: [`${this.$gettextInterpolate('Save failed  because of validation problems. Please check the %{invalidTabs}', { invalidTabs: this.invalidTabs.join(', ') })}  <i data-v-676ba8cf="" class="fa fa-times-circle fa-lg" style="color: red;"></i>`] },
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

		saveComments(data, url) {
			update(url, data).then((r) => {
				console.log(r)
			}).catch((e) => {
				this.$store.dispatch('setAlert', {
					$gettext: this.$gettext,
					message: e,
					variant: 'danger'
				})
			})
		},

		async submitData(tab, url) {
			console.log('submitData..................')
			this.$store.commit('setTabStatus', { tab: tab.name, value: 'saving' })
			let current_tab_data

			if (Array.isArray(tab.form_fields)) {
				current_tab_data = []
				tab.form_fields.forEach(form_field => {
					const save_obj = JSON.parse(JSON.stringify(tab.default_properties))
					for (const row in form_field) {
						save_obj[row] = form_field[row].selected
					}
					current_tab_data.push(save_obj)
				})
			}

			if (isObject(tab.form_fields)) {
				const save_obj = JSON.parse(JSON.stringify(tab.default_properties))
				current_tab_data = {}
				Object.keys(save_obj).forEach(key => { current_tab_data[key] = tab.form_fields[key].selected })
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

					this.$store.commit('setTabStatus', { tab: tab.name, value: true })

					if (Array.isArray(tab.form_fields)) {
						if (!tab.form_fields.length) {
							this.$store.commit('updateNewTabs', tab.name)
						}
					}
				}
			} catch (error) {
				this.$store.commit('setTabStatus', { tab: tab.name, value: false })
				console.log(error)
				this.$store.dispatch('setAlert', {
					$gettext: this.$gettext,
					message: { __all__: [this.$gettextInterpolate('Save failed for %{invalidTabs}', { invalidTabs: this.invalidTabs.join(', ') })] },
					variant: 'danger' })
			}
		}
	}
}
</script>
