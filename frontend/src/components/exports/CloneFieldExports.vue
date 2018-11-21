<template>
  <div v-if="field && tabName">
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

export default {

  props: {
    tabName: String,
    current_field: Object,
  },

  components: {
    Multiselect 
  },


  created(){
    this.field = JSON.parse(JSON.stringify(this.current_field))
  },

  computed: {
    countryOptions(){
      return this.$store.state.initialData.countryOptions
    },
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
        for(let existing_field of this.$store.state.form.tabs[this.tabName].form_fields) {
              if(current_field.substance.selected){
                if(existing_field.substance.selected === current_field.substance.selected  && existing_field[currentTypeOfCountryField].selected === country) {
                  fieldExists = true
                  break;
                }
              } else if(current_field.blend.selected) {
                if(existing_field.blend.selected === current_field.blend.selected  && existing_field[currentTypeOfCountryField].selected === country) {
                  fieldExists = true
                  break;
                }
              }
        }
        // substanceList, currentSectionName, groupName, currentSection, country, blend, prefillData
        if(!fieldExists) {
          
           this.$store.dispatch('createSubstance',{
                 substanceList: [current_field.substance.selected],
                 currentSectionName: this.tabName, 
                 groupName: current_field.group, 
                 country: country, 
                 blendList: [current_field.blend.selected], 
                 prefillData: null
                })
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