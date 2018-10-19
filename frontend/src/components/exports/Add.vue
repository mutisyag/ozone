<template>
  <div v-if="substances && countryOptions && section && currentSection">
    <div class="container">
      <h3>Add substances</h3>
      <h5>Filter Groups</h5>
      <multiselect @input="prepareSubstances" :multiple="true"  v-model="selected_groups.selected" :options="selected_groups.options" placeholder="Select annex group(s)"></multiselect>
      <hr>
      <multiselect :clear-on-select="false" :hide-selected="true" :close-on-select="false" class="mb-2" label="text" track-by="text" :multiple="true" placeholder="Select substance(s)" v-model="selected_substance.selected" @change="updateGroup($event)" :options="selected_substance.options"></multiselect>
      <hr>
      <b-btn @click="addSubstance" variant="success">Add rows</b-btn>
    </div>
  </div>
</template>

<script>

import Multiselect from 'vue-multiselect'
import fieldsPerTab from '@/mixins/fieldNamesPerTab.vue'

export default {

  props: {
    substances: null,
    section: null,
    currentSection: null,
    countryOptions: null,
  },

  components: {
    Multiselect 
  },

  mixins: [fieldsPerTab],

  mounted(){
    this.prepareGroups()
  },

  data() {
    return {
      selected_countries: {
        selected: null,
        options: this.countryOptions,
      },

      substancesOptions: [],

      selected_substance: {
        selected: null,
        group: null,
        options: [],
      },

      selected_groups: {
        selected: [],
        options: [],
      },

      group_field: {
        label: '',
        name: '',
        substance: null,
      },
    }
  },

  created(){
    console.log(this.section)
  },

  methods: {

    prepareSubstances(){
      this.selected_substance.options = []
        for(let substance of this.substances){
          if(this.selected_groups.selected.includes(substance.group.group_id)) {
            this.selected_substance.options.push(substance)
          }
        }
    },


    prepareGroups(){
      for(let substance of this.substances) {
          this.selected_groups.options.push(substance.group.group_id)
          //this.selected_groups.selected.push(group)
      }
      this.prepareSubstances()
    },

    updateGroup(selected_substance){
       for(let substance of this.substances) {
          if(selected_substance === substance.value) {
            this.group_field.label = substance.group.group_id
            this.group_field.name = substance.group.group_id
          }
      }
    },

    addSubstance() {
      for(let substance of this.selected_substance.selected) {
        this.updateGroup(substance.value)
        let substance_fields = {
          name: substance.value,
          options: this.substances,
          selected: substance,
          comments: [{
              name: "remarks_party",
              label: "Remarks (party)",
              selected: '',
              type: "text",
            },
            {
              name: "remarks_os",
              selected: '',
              type: "text",
              label: "Remarks (Secretariat)",
            },
          ],
          inner_fields: '',
        }

        let inner_fields = this.getInnerFields(this.currentSection, this.group_field.name)

        substance_fields.inner_fields = inner_fields
        this.group_field.substance = substance_fields
        console.log('section', this.section)
        var current_fields = this.section
        current_fields.push(this.group_field)
        this.section = current_fields

        this.group_field = {
          label: '',
          name: '',
          substance: null,
        }
      }
      this.resetData()
    },

    resetData() {

      this.selected_countries.selected = null

      this.group_field = {
        label: '',
        name: '',
        substance: null,
      }
    },

    removeSpecialChars(str) {
      return str.replace(/[^a-zA-Z0-9]+/g, "");
    },
  },

  watch: {
    substances: {
      handler: function(old_val, new_val) {
        this.prepareGroups()
      }
    }
  },

}
</script>

<style lang="css" scoped>
</style>