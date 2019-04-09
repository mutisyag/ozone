<template>
  <div>
    <div v-if="validField">
      <p v-translate>You are about to finalize this submission. Please check one of the options below</p>
      <hr>
      <fieldGenerator
        :fieldInfo="{index:final_flag, tabName: 'flags', field:final_flag}"
        :disabled="$store.getters.transitionState"
        :field="validField"
        :id="final_flag"
      ></fieldGenerator>
      <hr>
    </div>
    <p v-translate>Press OK to continue with the submission. Press Cancel to make further changes or corrections.</p>
  </div>
</template>

<script>
import fieldGenerator from '@/components/common/form-components/fieldGenerator'
import { getCommonLabels } from '@/components/common/dataDefinitions/labels'

export default {
  data() {
    return {
      labels: null
    }
  },
  created() {
    this.labels = getCommonLabels(this.$gettext)
  },
  components: {
    fieldGenerator
  },
  computed: {
    final_flag() {
      return Object.keys(this.formTabs.flags.default_properties).includes('flag_approved') ? 'flag_approved' : 'flag_valid'
    },
    formTabs() {
      return this.$store.state.form.tabs
    },
    validField() {
      return this.formTabs.flags && { ...this.formTabs.flags.form_fields[this.final_flag], type: 'radio' }
    }
  },
  methods: {
  },
  watch: {

  }
}
</script>

