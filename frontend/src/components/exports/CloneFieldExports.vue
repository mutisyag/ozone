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
      let typeOfCountryFields = ['destination_party', 'source_party', 'trade_party']

      for(let country of this.selected_countries.selected) {
        let current_field = JSON.parse(JSON.stringify(this.field))
        let substance = current_field.substance
              
        // substanceList, currentSectionName, groupName, currentSection, country, blend
        this.createSubstance([current_field.substance.selected], this.sectionName, current_field.group, this.section.form_fields, country, null, null)
      }

      // this.section.form_fields.splice(this.section.form_fields.indexOf(this.current_field),1)
      this.$emit('removeThisField')
      this.resetData()
      // this.$nextTick(() => {
        // this.$destroy()
      // });
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