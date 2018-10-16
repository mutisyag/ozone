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

  methods: {

    prepareSubstances(){
      this.selected_substance.options = []
      for(let group of this.substances) {
          for(let substance of group.substances){
            if(this.selected_groups.selected.includes(group.group_id)) {
              this.selected_substance.options.push({value: substance.id, text: substance.name, group: group})
            }
            this.substancesOptions.push({value: substance.id, text: substance.name, group: group})
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
       for(let group of this.substances) {
        for(let substance of group.substances){
          if(selected_substance === substance.id) {
            this.group_field.label = group.group_id
            this.group_field.name = group.group_id
            console.log(this.group_field)
          }
        }
      }
    },

    addSubstance() {
      for(let substance of this.selected_substance.selected) {
        this.updateGroup(substance.value)
        let substance_fields = {
          name: substance.value,
          options: this.substancesOptions,
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
            name: 'quantity_total_new',
            disabled: false,
            description: 'New',
            validation: 'numeric',
            type: 'number',
            selected: null,
          },
          {
            label: 'Total Quantity Exported for All Uses',
            name: 'quantity_total_recovered',
            description: 'Recovered and Reclaimed',
            disabled: false,
            type: 'number',
            validation: 'numeric',
            selected: null,
          },
          {
            label: 'Quantity of New Substances Exported as Feedstock',
            name: 'quantity_feedstock',
            description: '',
            disabled: false,
            type: 'number',
            validation: 'numeric',
            selected: null,
          },
          {
            label: 'Quantity of New Substances Exported for Exempted Essential and Critical Uses*',
            name: 'quantity_exempted',
            name_type: 'type_exempted',
            total_type: null,
            disabled: false,
            modalShow: false,
            description: 'Quantity',
            total: 0,
            type: 'multiple_fields',
            fields: [
              {
                label: 'Essential use, other than L&A',
                name: 'quantity_essential_uses',
                fields: [
                  {
                    label: "Quantity in metric",
                    name: "quantity_essential_uses",
                    validation: 'numeric',
                    selected: null,
                    type: "number",
                  },
                  {
                    label: "Decision",
                    name: "decision_essential_uses",
                    selected: null,
                    type: "text",
                  }
                ]
              }, 
              {
                label: 'Critical use',
                name: 'quantity_critical_uses',
                fields: [
                  {
                    label: "Quantity in metric",
                    name: "quantity_critical_uses",
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
                name: 'high_ambient_temperature',
                fields: [
                  {
                    label: "Quantity in metric",
                    name: "quantity_high_ambient_temperature",
                    validation: 'numeric',
                    selected: null,
                    type: "number",
                  },
                  {
                    label: "Decision",
                    name: "decision_high_ambient_temperature",
                    selected: null,
                    type: "text",
                  }
                ]
              }, 
              {
                  label: 'Process agent uses',
                  name: 'process_agent_uses',
                  fields: [
                    {
                      label: "Quantity in metric",
                      name: "quantity_process_agent_uses",
                      selected: null,
                      type: "text",
                    },
                    {
                      label: "Decision",
                      name: "decision_process_agent_uses",
                      selected: null,
                      type: "text",
                    }
                  ]
                }, 
              {
                label: 'Laboratory and analytical',
                name: 'laboratory_analytical_uses',
                fields: [
                  {
                    label: "Quantity in metric",
                    validation: 'numeric',
                    name: "quantity_laboratory_analytical_uses",
                    selected: null,
                    type: "number",
                  },
                  {
                    label: "Decision",
                    name: "decision_laboratory_analytical_uses",
                    selected: null,
                    type: "text",
                  }
                ]
              }, 
              {
                label: 'Quarantine and pre-shipment applications',
                name: 'quarantine_pre_shipment',
                fields: [
                  {
                    label: "Quantity in metric",
                    validation: 'numeric',
                    name: "quantity_quarantine_pre_shipment",
                    selected: null,
                    type: "number",
                  },
                  {
                    label: "Decision",
                    name: "decision_quarantine_pre_shipment",
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
                    name: "quantity_other",
                    selected: null,
                    type: "number",
                  },
                  {
                    label: "Decision",
                    name: "decision_other",
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