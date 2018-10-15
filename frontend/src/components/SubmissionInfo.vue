<template>
  <div v-if="info">
    <b-row>
      <b-col>
        <b-input-group size="sm" :prepend="info.party.label">
          <b-form-input v-validate="info.party.validation" :class="{'form-control': true, 'is-invalid': errors.has(info.party.name) }" :name="info.party.name" v-model="info.party.selected" :type="info.party.type" :disabled="info.party.disabled"></b-form-input>
        </b-input-group>
        <small v-show="errors.has(info.party.name)" class="error">{{ errors.first(info.party.name) }}</small>
      </b-col>

      <b-col>
        <b-input-group size="sm" :prepend="info.reporting_year.label">
          <b-form-input v-validate="info.reporting_year.validation" :class="{'form-control': true, 'is-invalid': errors.has(info.reporting_year.name) }" :name="info.reporting_year.name" v-model="info.reporting_year.selected" :type="info.reporting_year.type" :disabled="info.reporting_year.disabled"></b-form-input>
        </b-input-group>

        <small v-show="errors.has(info.reporting_year.name)" class="error">{{ errors.first(info.reporting_year.name) }}</small>
      </b-col>
    </b-row>

    <small>
       {{info.intro}}
    </small>
    <!-- <h2>{{info.title}}</h2> -->
            
    <form class="form-sections">
      <b-card>
        <div class="form-fields" v-for="field in info.form_fields" :key="field.name">
          <b-row class="field-wrapper">
            <b-col lg='3'>
              <label><b>{{field.label}}</b></label>
            </b-col>
            <b-col>
              <fieldGenerator :field.sync="field"></fieldGenerator>
            </b-col>
          </b-row>
       
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