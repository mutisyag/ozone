<script>
import { getLoginToken, removeLoginToken } from '@/components/common/services/login_api'

export default {

  methods: {
    login(evt) {
      evt.preventDefault()

      getLoginToken(this.form.username, this.form.password)
        .then((response) => {
          console.log(response.data)
          const date = new Date()

          date.setDate(date.getDate() + 30)
          this.$router.push({ name: 'Dashboard' })
        })
    },

    logout(cookie) {
      if (cookie === 'cookie') {
        this.$router.push({ name: 'Login' })
      } else {
        removeLoginToken().then(() => {
          console.log(this.$cookies)
          this.$router.push({ name: 'Login' })
        })
      }
    }
  }
}
</script>
