<template>
  <div v-if="section && field && inner_field && countryOptions">
    <div class="container">
      <div style="position: relative">
          <multiselect :max-height="250" :multiple="true" :clear-on-select="false" :hide-selected="true" :close-on-select="false" label="text" track-by="value" placeholder="Countries" v-model="selected_countries.selected" :options="countryOptions"></multiselect>
          <b-btn @click="addSubstance" v-if="selected_countries.selected">Add</b-btn>
      </div>
    </div>
  </div>
</template>

<script>

import Multiselect from 'vue-multiselect'

export default {

  props: {
    section: null,
    current_field: Object,
    inner_field: Object,
    countryOptions: Array,
  },

  components: {
    Multiselect 
  },

  created(){
    this.field = JSON.parse(JSON.stringify(this.current_field))
  },


  data() {
    return {
      substances: null,
      field: null,
      selected_countries: {
        selected: null,
      },
    }
  },


  methods: {

    addSubstance() {
      let exact_duplication = false
      if(this.selected_countries.selected.length === 1) {
         exact_duplication = true
      }
      for(let country of this.selected_countries.selected) {
        let current_field;
        if(!exact_duplication){
          current_field = JSON.parse(JSON.stringify(this.field))
        } else {
          current_field = JSON.parse(JSON.stringify(this.current_field))
        }
        for(let fields of current_field.substance.inner_fields) {
            if(['destination_party','source_party', 'trade_party'].includes(fields.name)){
              fields.duplicate = false
              fields.selected = country
            }
        }
        if(current_field.name === 'blend') {
          current_field.expand = false
        }
        
        this.section.form_fields.push(current_field)
      }

      this.section.form_fields.splice(this.section.form_fields.indexOf(this.current_field),1)
      
      this.resetData()
    },

    resetData() {
      this.selected_countries.selected = null
    },

    removeSpecialChars(str) {
      return str.replace(/[^a-zA-Z0-9]+/g, "");
    },
  },

}
</script>

<style lang="css" scoped>
</style>