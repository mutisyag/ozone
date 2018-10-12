<template>
  <div v-if="substances && countryOptions && section">
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

export default {

  props: {
    substances: null,
    section: null,
    countryOptions: null,
  },

  components: {
    Multiselect 
  },

  mounted(){
    this.prepareGroups()
  },

  data() {
    return {
      selected_countries: {
        selected: null,
        options: this.countryOptions,
      },

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

  methods: {

    prepareSubstances(){
      this.selected_substance.options = []
      for(let group of this.substances) {
        console.log(group)
        if(this.selected_groups.selected.includes(group.group_id)) {
          for(let substance of group.substances){
            this.selected_substance.options.push({value: substance, text: substance, group: group})
          }
        }
      }
    },

    prepareGroups(){
      for(let group of this.substances) {
          this.selected_groups.options.push(group.group_id)
          //this.selected_groups.selected.push(group)
      }
      this.prepareSubstances()
    },

    updateGroup(selected_substance){
      console.log(selected_substance)
       for(let group of this.substances) {
        for(let substance of group.substances){
          if(selected_substance === substance) {
            this.group_field.label = group.group_id
            this.group_field.name = this.removeSpecialChars(group.group_id)
          }
        }
      }
    },

    addSubstance() {
      for(let substance of this.selected_substance.selected) {
        this.updateGroup(substance.value)
        let substance_fields = {
          get label () { return this.selected.value} ,
          name: this.removeSpecialChars(substance.value),
          options: this.selected_substance.options,
          selected: substance,
          comments: [{
              name: "party_remarks",
              label: "Remarks (party)",
              selected: '',
              type: "text",
            },
            {
              name: "secretariat_remarks",
              selected: '',
              type: "text",
              label: "Remarks (Secretariat)",
            },
          ],
          inner_fields: '',
        }

        let inner_fields = [
          {
            label: 'Country of Destination of Exports**',
            name: 'country_of_destination_exports',
            description: '',
            type: 'select',
            duplicate: true,
            selected: null,
            options: this.countryOptions,
          },
          {
            label: 'Total Quantity Exported for All Uses',
            name: 'total_import_quantity_all_uses_new',
            disabled: false,
            description: 'New',
            validation: 'numeric',
            type: 'number',
            selected: null,
          },
          {
            label: 'Total Quantity Exported for All Uses',
            name: 'total_import_quantity_all_uses_recovered',
            description: 'Recovered and Reclaimed',
            disabled: false,
            type: 'number',
            validation: 'numeric',
            selected: null,
          },
          {
            label: 'Quantity of New Substances Exported as Feedstock',
            name: 'import_quantity_new_substances_as_feedstock',
            description: '',
            disabled: false,
            type: 'number',
            validation: 'numeric',
            selected: null,
          },
          {
            label: 'Quantity of New Substances Exported for Exempted Essential and Critical Uses*',
            name: 'quantity_import_exempted_essential_critical_uses',
            disabled: false,
            modalShow: false,
            description: 'Quantity',
            total: 0,
            type: 'multiple_fields',
            fields: [
              {
                label: 'Essential use, other than L&A',
                name: 'essential_use',
                fields: [
                  {
                    label: "Quantity in metric",
                    name: "quantity_in_metric",
                    validation: 'numeric',
                    selected: null,
                    type: "number",
                  },
                  {
                    label: "Decision",
                    name: "decision",
                    selected: null,
                    type: "text",
                  }
                ]
              }, 
              {
                label: 'Critical use',
                name: 'critical_use',
                fields: [
                  {
                    label: "Quantity in metric",
                    name: "quantity_in_metric",
                    validation: 'numeric',
                    selected: null,
                    type: "number",
                  },
                  {
                    label: "Decision",
                    name: "decision",
                    selected: null,
                    type: "text",
                  }
                ]
              }, 
              {
                label: 'High ambient temperature',
                name: 'high_ambient_temp',
                fields: [
                  {
                    label: "Quantity in metric",
                    name: "quantity_in_metric",
                    validation: 'numeric',
                    selected: null,
                    type: "number",
                  },
                  {
                    label: "Decision",
                    name: "decision",
                    selected: null,
                    type: "text",
                  }
                ]
              }, 
              {
                label: 'Laboratory and analytical',
                name: 'lab_analytical',
                fields: [
                  {
                    label: "Quantity in metric",
                    validation: 'numeric',
                    name: "quantity_in_metric",
                    selected: null,
                    type: "number",
                  },
                  {
                    label: "Decision",
                    name: "decision",
                    selected: null,
                    type: "text",
                  }
                ]
              }, 
              {
                label: 'Quarantine and pre-shipment applications',
                name: 'quarantine_pre_shipment_apl',
                fields: [
                  {
                    label: "Quantity in metric",
                    validation: 'numeric',
                    name: "quantity_in_metric",
                    selected: null,
                    type: "number",
                  },
                  {
                    label: "Decision",
                    name: "decision",
                    selected: null,
                    type: "text",
                  }
                ]
              }, 
               {
                label: 'Other/Unspecified',
                name: 'other',
                fields: [
                  {
                    label: "Quantity in metric",
                    validation: 'numeric',
                    name: "quantity_in_metric",
                    selected: null,
                    type: "number",
                  },
                  {
                    label: "Decision",
                    name: "decision",
                    selected: null,
                    type: "text",
                  }
                ]
              }, 
            ]
          },
        ]

        substance_fields.inner_fields = inner_fields
        this.group_field.substance = substance_fields

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