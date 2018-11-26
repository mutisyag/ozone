<template>
  <div class="animated fadeIn">
      <dataManager :submission="$route.query.submission"></dataManager>
  </div>
</template>

<script>
import dataManager from '../components/DataManager.vue'

export default {
  name: 'form',
  components: {
    dataManager
  },
  data: function () {
    return {}
  },


  beforeRouteLeave (to, from, next) {
    this.$destroy()
    next()
  },

  methods: {
  }
}
</script>

<style>

</style>
