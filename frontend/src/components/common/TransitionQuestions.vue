<template>
  <div>
    <b-modal size="lg" ref="transition_modal" id="transition_modal">
      <div slot="modal-title"><i class="fa fa-exclamation-circle"></i>&nbsp; <span v-translate>Please confirm</span></div>
      <Submit :skipArt7Specific="skipArt7Specific" v-if="transition === 'submit'"/>
      <Process v-else-if="transition === 'process'"/>
      <Recall v-else-if="transition === 'recall'"/>
      <Finalize v-else-if="transition === 'finalize'"/>
      <Reinstate v-else-if="transition === 'unrecall_to_finalized'"/>
      <div v-else>
        <p v-translate>You are about to change the state of the submission.</p>
        <p v-translate>Press OK to continue with the submission. Press Cancel to make further changes or corrections.</p>
      </div>
      <div slot="modal-footer">
        <b-btn class="mr-2" @click="$refs.transition_modal.hide()" variant="light">
          <span v-translate>Cancel</span>
        </b-btn>
        <b-btn :disabled="disableOkButton" @click="doTransition" variant="primary">Ok</b-btn>
      </div>
    </b-modal>
  </div>
</template>

<script>
import Submit from '@/components/common/transitionQuestions/Submit'
import Process from '@/components/common/transitionQuestions/Process'
import Recall from '@/components/common/transitionQuestions/Recall'
import Finalize from '@/components/common/transitionQuestions/Finalize'
import Reinstate from '@/components/common/transitionQuestions/Reinstate'

export default {
  props: {
    transition: String,
    submission: String,
    skipArt7Specific: Boolean
  },
  components: {
    Submit,
    Process,
    Recall,
    Finalize,
    Reinstate
  },
  data() {
    return {
      labels: {},
      transitionToValidate: ['submit'],
      noForwardToDashboard: ['process']
    }
  },
  computed: {
    disableOkButton() {
      if (this.transition === 'finalize' && this.hasValidFlag && this.$store.state.form.tabs.flags.form_fields.flag_valid.selected === null) {
        return true
      }
      return false
    },
    hasValidFlag() {
      return this.$store.state.form.tabs.flags && this.$store.state.form.tabs.flags.form_fields.flag_valid
    }
  },
  mounted() {
    this.$root.$on('bv::modal::hide', (bvEvent, modalId) => {
      if (modalId === 'transition_modal') {
        this.$emit('removeTransition')
      }
    })
  },
  methods: {
    doTransition() {
      // console.log(this.transition)
      if (this.transition === 'finalize') {
        this.$store.commit('setTabStatus', { tab: 'flags', value: true })
      }
      this.$store.dispatch('triggerSave', { action: 'doSubmissionTransition', data: { $gettext: this.$gettext, submission: this.submission, transition: this.transition, noModal: true, backToDashboard: !this.noForwardToDashboard.includes(this.transition) } })
      this.$refs.transition_modal.hide()
    }
  },
  watch: {
    transition: {
      handler(val) {
        if (val !== null) {
          if (this.transitionToValidate.includes(val)) {
            this.$store.dispatch('triggerSave', { action: '', data: { submission: this.submission, transition: `before-${this.transition}`, nextTransition: this.transition } })
            if (this.$store.state.dataForAction === null) {
              this.$emit('removeTransition')
            } else {
              this.$refs.transition_modal.show()
            }
          } else {
            this.$refs.transition_modal.show()
          }
        }
      }
    }
  }
}
</script>

