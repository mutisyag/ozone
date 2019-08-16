<script>
import SaveMixin from '@/components/common/mixins/SaveMixin'

export default {
  mixins: [SaveMixin],
  methods: {
    prepareDataForSave() {
      const justSave = []
      const removeDataAndSave = []
      const doNotSave = []

      Object.values(this.form.tabs).filter(tab => tab.hasOwnProperty('form_fields')).forEach(async tab => {
        const url = this.$store.state.current_submission[tab.endpoint_url]
        if (!doNotSave.includes(tab.name)) {
          if (justSave.includes(tab.name)) {
            await this.submitData(tab, url)
            this.checkIfThereIsAnotherActionToDoBeforeReturning(tab.name)
          } else if (removeDataAndSave.includes(tab.name)) {
            this.$store.dispatch('removeDataFromTab', tab.name).then(async () => {
              await this.submitData(tab, url)
              this.checkIfThereIsAnotherActionToDoBeforeReturning(tab.name)
            })
          } else {
            await this.submitData(tab, url)
            this.checkIfThereIsAnotherActionToDoBeforeReturning(tab.name)
          }
        }
      })
    }
  }
}
</script>
