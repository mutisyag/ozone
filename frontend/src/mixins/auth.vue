<template>
</template>

<script>
import { getLoginToken, removeLoginToken } from '@/api/login_api.js';

export default {

  methods: {
    login(evt) {
      evt.preventDefault();

      getLoginToken(this.form.username, this.form.password)
      .then((response) => {
        console.log(response.data)
          let date = new Date();

      date.setDate(date.getDate() + 30);
      this.$cookies.set('authToken', response.data.token, date);
      this.$router.push({ name: 'Dashboard' });
      })
    },

    logout() {
      removeLoginToken().then((response)=> {
        console.log(this.$cookies)
        this.$cookies.remove('authToken');
        this.$router.push({ name: 'Login' });
      });
    },
  },
}
</script>

<style>
</style>