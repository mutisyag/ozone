<script>
import SaveMixin from '@/components/common/mixins/SaveMixin'

export default {
	mixins: [SaveMixin],
	methods: {
		alertUnsavedData(tabName, tab, url) {
			const answer = window.confirm(`${tabName}: ${this.$gettext('You have unsaved data that will be deleted because of the "No" selected in questionnaire for that specific section. Are you sure yo want to save that form ?')}`)
			if (answer) {
				this.$store.dispatch('removeDataFromTab', tabName).then(() => {
					this.submitData(tab, url)
				})
				return true
			}
			// this.$store.dispatch('setAlert', {
			// 	$gettext: this.$gettext,
			// 	message: { __all__: [`${tabName}: ${this.$gettext('Data was not saved')}`] },
			// 	variant: 'danger' })
			// this.$store.commit('setTabStatus', { tab: tabName, value: false })
			return false
		},

		prepareDataForSave() {
			const justSave = []
			const removeDataAndSave = []
			const doNotSave = []
			Object.values(this.form.tabs.questionaire_questions.form_fields).forEach(questionnaire_field => {
				if (questionnaire_field.selected && !this.invalidTabs.includes(questionnaire_field.name)) {
					justSave.push(questionnaire_field.name)
				}
				if (!questionnaire_field.selected && this.$store.state.form.tabs[questionnaire_field.name].form_fields.length) {
					removeDataAndSave.push(questionnaire_field.name)
				}
				if (!questionnaire_field.selected
						&& !this.$store.state.form.tabs[questionnaire_field.name].form_fields.length
						&& this.newTabs.includes(questionnaire_field.name)) {
					doNotSave.push(questionnaire_field.name)
				}
			})
			let stopSave = false
			Object.values(this.form.tabs).filter(tab => tab.hasOwnProperty('form_fields')).forEach(tab => {
				const url = this.$store.state.current_submission[tab.endpoint_url]
				if (removeDataAndSave.includes(tab.name)) {
					if (!this.alertUnsavedData(tab.name, tab, url)) {
						stopSave = true
					} else {
						stopSave = false
					}
				}
			})
			if (!stopSave) {
				Object.values(this.form.tabs).filter(tab => tab.hasOwnProperty('form_fields')).forEach(tab => {
					const url = this.$store.state.current_submission[tab.endpoint_url]
					if (!doNotSave.includes(tab.name)) {
						if (justSave.includes(tab.name)) {
							this.submitData(tab, url)
						} else {
							url && this.submitData(tab, url)
						}
					}
				})
			}
		}
	}
}
</script>
