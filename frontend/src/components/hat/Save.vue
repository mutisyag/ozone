<script>
import SaveMixin from '@/components/common/mixins/SaveMixin'

export default {
  mixins: [SaveMixin],
  methods: {
  prepareDataForSave() {
      this.tabsToSave = Object.values(this.form.tabs).filter(tab => tab.hasOwnProperty('form_fields') && tab.hasOwnProperty('endpoint_url') && tab.status === 'edited').map(t => t.name)
      Object.values(this.form.tabs).filter(tab => tab.hasOwnProperty('form_fields') && tab.hasOwnProperty('endpoint_url')).forEach(async tab => {
        const url = this.$store.state.current_submission[tab.endpoint_url]
        await this.submitData(tab, url)
        this.checkIfThereIsAnotherActionToDoBeforeReturning(tab.name)
      })
    }
  }
}
</script>
