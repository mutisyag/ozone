<template>
    <b-btn
			@click="validation"
			style="border-top-right-radius: 0;border-bottom-right-radius:0"
			variant="outline-success">
        Save
    </b-btn>
</template>

<script>

import { post, update } from '@/components/common/services/api'
import { isObject } from '@/components/common/services/utilsService'

export default {

	name: 'Save',

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
					message: { __all__: [`Save failed  because of validation problems. Please check the ${this.invalidTabs.join(', ')} <i data-v-676ba8cf="" class="fa fa-times-circle fa-lg" style="color: red;"></i>`] },
					variant: 'danger'
				})
			} else {
				this.prepareDataForSave()
			}
		},

		submitData(tab, url) {
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
			if (this.newTabs.includes(tab.name)) {
				post(url, current_tab_data).then(() => {
					this.$store.commit('setTabStatus', { tab: tab.name, value: true })
					if (tab.form_fields.length) {
						this.$store.commit('tabHasBeenSaved', tab.name)
					} else {
						this.$store.commit('updateNewTabs', tab.name)
					}
				}).catch((error) => {
					this.$store.commit('setTabStatus', { tab: tab.name, value: false })
					console.log(error.response)
					this.$store.dispatch('setAlert', {
						message: { __all__: [`Save failed for ${this.invalidTabs}`] },
						variant: 'danger' })
				})
			}
			if (!this.newTabs.includes(tab.name)) {
				update(url, current_tab_data).then(() => {
					this.$store.commit('setTabStatus', { tab: tab.name, value: true })
					if (Array.isArray(tab.form_fields)) {
						if (!tab.form_fields.length) {
							this.$store.commit('updateNewTabs', tab.name)
						}
					}
				}).catch(() => {
					this.$store.commit('setTabStatus', { tab: tab.name, value: false })
					this.$store.dispatch('setAlert', {
						message: { __all__: [`Save failed for ${this.invalidTabs}`] },
						variant: 'danger'
					})
				})
			}
		}

	}
}
</script>
