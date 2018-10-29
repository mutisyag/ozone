<template>
  <div v-if="info && tabs">

    <small>
       {{info.intro}}
    </small>
    <!-- <h2>{{info.title}}</h2> -->
            
    <form class="form-sections">
      <b-card>
        <div class="form-fields" v-for="field in info.form_fields" :key="field.name">
          <div class="field-wrapper">
            <label>{{field.label}}</label>
            <fieldGenerator :tab.sync="tabs" :field.sync="field"></fieldGenerator>
          </div>
        </div>
      </b-card>
    </form> 

    </div>
</template>

<script>

import fieldGenerator from "./fieldGenerator";

export default {

  name: 'Tab1',

  props: {
    info: Object,
    tabs: Object,
  },


  created(){
    // this.tabs.push('asd')
  },

  components: {fieldGenerator},

  data () {
    return {

    }
  },

  methods: {
  },


}
</script>

<style lang="css" scoped>

</style>