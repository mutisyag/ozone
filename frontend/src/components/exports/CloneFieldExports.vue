<template>
  <div v-if="section && field && countryOptions && sectionName">
    <div class="container">
      <div style="position: relative">
          <multiselect :max-height="250" :multiple="true" :clear-on-select="false" :hide-selected="true" :close-on-select="false" label="text" trackBy="value" placeholder="Countries" v-model="selected_countries.selected" :options="countryOptions"></multiselect>
          <b-btn @click="addSubstance" v-if="selected_countries.selected">Add</b-btn>
      </div>
    </div>
  </div>
</template>
<script>

// import Multiselect from 'vue-multiselect'
import Multiselect from '@/mixins/modifiedMultiselect'
import createSubstance from '@/mixins/createSubstance.vue'

export default {

  props: {
    section: null,
    current_field: Object,
    sectionName: String,
    countryOptions: Array,
  },

  components: {
    Multiselect 
  },

  mixins: [createSubstance],

  created(){
    this.field = JSON.parse(JSON.stringify(this.current_field))
  },



  data() {
    return {
      field: null,
      selected_countries: {
        selected: null,
      },
    }
  },


  methods: {

    addSubstance() {
      let current_field = JSON.parse(JSON.stringify(this.field))
      let typeOfCountryFields = ['destination_party', 'source_party', 'trade_party']
      let currentTypeOfCountryField = ''

      for(let type of typeOfCountryFields){
        if(current_field.hasOwnProperty(type)) currentTypeOfCountryField =  type 
      }

      for(let country of this.selected_countries.selected) {
        let fieldExists = false
        for(let existing_field of this.section.form_fields) {
              if(existing_field.substance.selected === current_field.substance.selected  && existing_field[currentTypeOfCountryField].selected === country) {
                fieldExists = true
                break;
              }
        }
        // substanceList, currentSectionName, groupName, currentSection, country, blend, prefillData
        if(!fieldExists) {
          this.createSubstance([current_field.substance.selected], this.sectionName, current_field.group, this.section.form_fields, country, [current_field.blend.selected], null)
        }

      }
      this.$emit('removeThisField')
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