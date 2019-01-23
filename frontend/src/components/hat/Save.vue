<script>
import SaveMixin from '@/components/common/mixins/SaveMixin'

export default {
	mixins: [SaveMixin],
	methods: {
		prepareDataForSave() {
			Object.values(this.form.tabs).filter(tab => tab.hasOwnProperty('form_fields') && tab.hasOwnProperty('endpoint_url')).forEach(tab => {
				const url = this.$store.state.current_submission[tab.endpoint_url]
				this.submitData(tab, url)
			})
		}
	}
}
</script>
