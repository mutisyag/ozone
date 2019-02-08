<script>
import SaveMixin from '@/components/common/mixins/SaveMixin'

export default {
	mixins: [SaveMixin],
	methods: {
		prepareDataForSave() {
			console.log('prepareDataForSave00')
			const justSave = []
			const removeDataAndSave = []
			const doNotSave = []

			Object.values(this.form.tabs).filter(tab => tab.hasOwnProperty('form_fields')).forEach(tab => {
				const url = this.$store.state.current_submission[tab.endpoint_url]
				if (!doNotSave.includes(tab.name)) {
					if (justSave.includes(tab.name)) {
						this.submitData(tab, url)
					} else if (removeDataAndSave.includes(tab.name)) {
						this.$store.dispatch('removeDataFromTab', tab.name).then(() => {
							this.submitData(tab, url)
						})
					} else {
						this.submitData(tab, url)
					}
				}
			})
		}
	}
}
</script>
