<template>
  <div>
    <tabsmanager v-if="initialDataReady" :submission="submission"/>
  </div>
</template>

<script>
import tabsManager from '@/components/raf/TabsManager'
import dataManagerMixin from '@/components/common/mixins/DataManagerMixin'

export default {
  name: 'DataManager',
  components: {
    tabsmanager: tabsManager
  },
  mixins: [dataManagerMixin],

  methods: {
    doInitialStuff() {
      if (!this.submission) {
        this.$router.push({ name: 'Dashboard' })
      } else {
        if (process.env.NODE_ENV !== 'development') {
          window.addEventListener('beforeunload', this.alertUnsavedData)
        }
        this.$store.dispatch('getInitialData', {
          $gettext: this.$gettext,
          submission: this.submission,
          formName: this.currentFormName,
          additionalAction: 'getEssenCritTypes'
        }).then(() => {
          this.prePrefill()
          this.prefillComments()
        })
      }
    }
  }

}
</script>
