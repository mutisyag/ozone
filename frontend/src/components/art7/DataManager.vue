<template>
  <div>
    <tabsmanager v-if="initialDataReady" :submission="submission"/>
  </div>
</template>

<script>
import tabsManager from '@/components/art7/TabsManager'
import dataManagerMixin from '@/components/common/mixins/DataManagerMixin'
import {
  isObject,
  getPropertyValue
} from '@/components/common/services/utilsService'

export default {
  name: 'DataManager',
  components: {
    tabsmanager: tabsManager
  },
  mixins: [dataManagerMixin],
  initialDataReady() {
    this.$store.commit('setPreventLeaveConfirm', false)
    if (!this.form) {
      return false
    }
    for (const propertyPath of this.form.formDetails.dataNeeded) {
      const propValue = getPropertyValue(this.$store.state, propertyPath)
      if (propertyPath === 'submissionDefaultValues.submission_format') {
        // eslint-disable-next-line no-continue
        continue
      }
      if (!propValue) return false
    }
    const { dataNeeded } = this.form.formDetails
    Object.values(this.form.tabs).forEach(tab => {
      if (isObject(tab.form_fields)) {
        for (const formFieldPropName in tab.form_fields) {
          const formField = tab.form_fields[formFieldPropName]
          if (formField.optionsStatePropertyPath) {
            for (const propertyPath of dataNeeded) {
              if (formField.optionsStatePropertyPath === propertyPath) {
                const propValue = getPropertyValue(this.$store.state, propertyPath)
                formField.options = propValue
                break
              }
            }
          }
          if (formField.selectedPropertyPath) {
            for (const propertyPath of dataNeeded) {
              if (formField.selectedPropertyPath === propertyPath) {
                const propValue = getPropertyValue(this.$store.state, propertyPath)
                if (formField.selected !== propValue) {
                  formField.selected = propValue
                }
                break
              }
            }
          }
        }
      }
    })
    return this.prefilled
  }
}
</script>
