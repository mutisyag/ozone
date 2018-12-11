<template>
    <b-btn @click="validation" style="border-top-right-radius: 0;border-bottom-right-radius:0" variant="outline-success">
        Save
      </b-btn>
</template>

<script>

import { post, update } from '@/components/common/services/api'

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
	methods: {
		pushUnique(array, item) {
			if (array.indexOf(item) === -1) {
				array.push(item)
			}
		},
		validation() {
			this.invalidTabs = []
			const tabsToValidate = Object.values(this.$store.state.form.tabs).filter(tab => tab.validate).map(tab => tab.name)
			for (const tab of tabsToValidate) {
				for (const field of this.$store.state.form.tabs[tab].form_fields) {
					if (field.validation.selected.length) {
						this.invalidTabs.push(this.$store.state.form.tabs[tab].name)
						this.$store.commit('setTabStatus', { tab, value: false })
						break
					}
				}
			}
			if (this.invalidTabs.length) {
				this.$store.dispatch('setAlert', {
					message: { __all__: [`Save failed for ${this.invalidTabs.join(', ')} because of validation problems. Please check the data in the forms marked with <i data-v-676ba8cf="" class="fa fa-times-circle fa-lg" style="color: red;"></i>`] },
					variant: 'danger'
				})
			}
			this.submitQuestionaireData('questionaire_questions')
		},

		submitQuestionaireData(field) {
			this.$store.commit('setTabStatus', { tab: 'questionaire_questions', value: 'saving' })
			const current_tab = Object.values(this.$store.state.form.tabs).find((value) => value.name === field)
			const save_obj = JSON.parse(JSON.stringify(current_tab.default_properties))
			Object.values(current_tab.form_fields).forEach(form_field => {
				save_obj[form_field.name] = form_field.selected
			})

			post(this.$store.state.current_submission[current_tab.endpoint_url], save_obj).then(() => {
				this.$store.commit('setTabStatus', { tab: 'questionaire_questions', value: true })

				for (const questionnaire_field of Object.values(this.$store.state.form.tabs.questionaire_questions.form_fields)) {
					if (questionnaire_field.selected && !this.invalidTabs.includes(questionnaire_field.name)) {
						this.submitData(questionnaire_field.name)
					} else if (!questionnaire_field.selected && this.$store.state.form.tabs[questionnaire_field.name].form_fields.length) {
						this.$store.dispatch('removeDataFromTab', questionnaire_field.name).then(() => {
							this.submitData(questionnaire_field.name)
						})
					}
				}
				this.submitData('sub_info')
			}).catch((error) => {
				this.$store.dispatch('setAlert', {
					message: { __all__: ['Please complete the questionnaire before saivng'] },
					variant: 'danger'
				})
				this.$store.commit('setTabStatus', { tab: 'questionaire_questions', value: false })
				console.log(error)
			})
		},

		submitData(field) {
			const current_tab = this.$store.state.form.tabs[field]
			if (this.$store.state.newTabs.indexOf(field) === -1) {
				current_tab.status = 'saving'
				let current_tab_data = []
				current_tab.form_fields.forEach(form_field => {
					const save_obj = JSON.parse(JSON.stringify(current_tab.default_properties))

					for (const field2 in form_field) {
						save_obj[field2] = form_field[field2].selected
					}

					current_tab_data.push(save_obj)
				})
				if (current_tab.name === 'sub_info') {
					current_tab_data = current_tab_data[0]
				}
				update(`${this.$store.state.current_submission[current_tab.endpoint_url]}${current_tab.endpoint_additional_url ? current_tab.endpoint_additional_url : ''}`, current_tab_data).then(() => {
					current_tab.status = true
					if (current_tab_data.length) {
						this.$store.commit('tabHasBeenSaved', field)
					} else {
						this.$store.commit('updateNewTabs', field)
					}
				}).catch((error) => {
					current_tab.status = false
					console.log(error.response)
					this.invalidTabs.push(field)
					this.$store.dispatch('setAlert', {
						message: { __all__: [`Save failed for ${this.invalidTabs}`] },
						variant: 'danger' })
				})
			} else if (this.$store.state.newTabs.indexOf(field) !== -1 && current_tab.form_fields.length) {
				current_tab.status = 'saving'

				const current_tab_data = []

				current_tab.form_fields.forEach(form_field => {
					const save_obj = JSON.parse(JSON.stringify(current_tab.default_properties))

					for (const field2 in form_field) {
						save_obj[field2] = form_field[field2].selected
					}

					current_tab_data.push(save_obj)
				})

				post(this.$store.state.current_submission[current_tab.endpoint_url], current_tab_data).then(() => {
					current_tab.status = true
					this.$store.commit('tabHasBeenSaved', field)
				}).catch(() => {
					current_tab.status = false
					this.invalidTabs.push(field)
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

<style lang="css" scoped>

.alert b {
  margin-right: 1rem;
}

</style>
