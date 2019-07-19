<template>
  <b-modal
    id="inactivity_modal"
    ref="inactivity_modal"
    @hide="stopInactivityTimer"
    :title="$gettext('You are inactive')"
    hide-footer
  >
    <h4 class="text-center">
        <span v-translate>You will be disconnected from the application in:</span> <br>
    </h4>
    <h1 class="text-center">
        {{convertMS(this.inactivyTimer).minute}}:{{convertMS(this.inactivyTimer).seconds}}
    </h1>
    <b-btn class="mt-4 mb-3" @click="$refs.inactivity_modal.hide()" variant="primary" block size="lg">Stop timer</b-btn>
  </b-modal>
</template>
<script>
import auth from '@/components/common/mixins/auth'
import {
  apiBase
} from '@/components/common/services/api.js'

export default {
  data() {
    return {
      time: 0,
      inactivyTimer: 60,
      interval: null
    }
  },
  mixins: [auth],

  mounted() {
    window.addEventListener('load', this.resetTimer, true)
    const events = [
      'mousedown',
      'mousemove',
      'keypress',
      'scroll',
      'touchstart'
    ]
    events.forEach(name => {
      document.addEventListener(name, this.resetTimer, true)
    })
  },

  methods: {
    convertMS(seconds) {
      let minute
      minute = Math.floor(seconds / 60)
      seconds %= 60
      minute %= 60
      return {
        minute,
        seconds
      }
    },
    startInactivityTimer() {
      this.$refs.inactivity_modal.show()
      this.interval = setInterval(this.timerIncrement, 1000)
    },
    stopInactivityTimer() {
      clearInterval(this.interval)
      this.inactivyTimer = 60
      this.$refs.inactivity_modal.hide()
    },

    timerIncrement() {
      if (this.inactivyTimer > 0) {
        this.inactivyTimer -= 1
      }
      if (this.inactivyTimer === 0) {
        this.$store.commit('setPreventLeaveConfirm', true)
        this.logout()
        this.resetTimer()
        window.location = `${apiBase}/admin/login/?next=${encodeURIComponent(window.location.origin)}/reporting`
      }
    },
    resetTimer() {
      clearTimeout(this.time)
      //   300000 = 5 minutes
      this.time = setTimeout(this.startInactivityTimer, 300000)
    }
  }
}
</script>
