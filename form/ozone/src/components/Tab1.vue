<template>
  <div v-if="info && tabs">

    <small>
       {{info.intro}}
    </small>
    <!-- <h2>{{info.title}}</h2> -->
            
    <form class="form-sections">
      <b-card :key="section.name" v-for="section in info.form_sections">
        <h4>{{section.title}}</h4>
        <div class="form-fields" v-for="field in section.form_fields" :key="field.name">
          <b-row class="field-wrapper" v-if="section.name != 'questionnaire'">
            <b-col lg='3'>
              <label><b>{{field.label}}</b></label>
            </b-col>
            <b-col>
              <fieldGenerator :field.sync="field"></fieldGenerator>
            </b-col>
          </b-row>
          <div class="field-wrapper" v-else>
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