
const saveWatcher = {
  computed: {
    saved() {
      return this.$store.state.saveSuccess.indexOf(this._uid)
    }
  },
  methods: {
    triggerSave(callFunctionAfterSaveisDone) {
      this.$store.dispatch('triggerSave', { action: 'confirmSaveDone', data: this._uid })
      // create a new watcher every time this is called
      const watcher = this.$watch('saved', (newVal, oldVal) => {
        if (oldVal !== newVal && newVal !== -1) {
          this.$store.commit('removeSaveSuccess', this._uid)
          if (callFunctionAfterSaveisDone instanceof Function) {
            callFunctionAfterSaveisDone()
          }
          // remove the watcher
          watcher()
        }
      })
    }
  }
}

export default saveWatcher
