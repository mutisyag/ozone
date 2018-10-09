<template>
  <div>
    <tabsmanager :data="form"></tabsmanager>
  </div>
</template>

<script>

import tabsManager from './TabsManager'
import form from '../assets/form.js'


export default {
  name: 'DataManager',
  components: {
    tabsmanager:tabsManager
  },

  created() {
  },

  data () {
    return {
      form: JSON.parse(JSON.stringify(form))
    }
  },

  methods: {

  },


}
</script>

<style lang="css" scoped>
</style>