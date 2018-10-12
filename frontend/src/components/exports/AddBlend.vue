<template>
  <div v-if="substances && section && blends && countryOptions">
    <div class="container">

     
        <div class="mt-2 mb-2" style="display: flex;">
          <multiselect track-by="id"  :clear-on-select="false" :hide-selected="true" :close-on-select="false" :multiple="true" label="name" v-model="selected_blends.selected" @input="new_blend = null" placeholder="Select predefined blend" :options="selected_blends.options"></multiselect>
          <div class="add-blend-wrapper"><b>/</b> <b-btn style="margin-left: .5rem" variant="primary" @click="addNewBlend">Add new blend</b-btn></div>
        </div>


        <div :key="blend.name" v-if="selected_blends.selected" v-for="blend in selected_blends.selected">
          <h5>Composition of <b>{{blend.name}}</b></h5>
          <b-row v-for="substance in blend.composition">
            <b-col>{{substance.name}}</b-col>
            <b-col>{{substance.percent.toLocaleString("en", {style: "percent"})}}</b-col>
          </b-row>
        </div>
      
       <div v-if="new_blend">
          <h5>Composition</h5>
          <b-input-group prepend="Blend name">
            <b-form-input type="text" v-model="new_blend.name"></b-form-input>
            <b-input-group-append>
              <b-btn variant="default" @click="addSubstanceToBlend">+</b-btn>
            </b-input-group-append>
          </b-input-group>
          <b-input-group class="mb-2 mt-2" v-for="substance in new_blend.composition">
              <b-input-group-prepend>
                <b-btn  style="z-index:initial;"  variant="danger" @click="removeSubstanceFromBlend(substance)">X</b-btn>
              </b-input-group-prepend>

              <multiselect label="text" track-by="text" placeholder="Substance" v-model="substance.name" :options="selected_substance.options"></multiselect>
              <b-input-group-append>
                <b-form-input type="text" placeholder="%" v-model="substance.percent"></b-form-input>
              </b-input-group-append>
          </b-input-group>
          <small>Note: If a non standard blend not listed in section 11 of the data reporting instructions and guidelines is to be reported, please indicate the percentage by weight of each constituent controlled substance of the mixture being reported in the “comments” box above.</small>
        </div>

      <hr>
      <b-btn v-if="selected_blends.selected" @click="addSubstance('selected')" variant="success">Add selected blends</b-btn>
      <b-btn v-if="new_blend" @click="addSubstance('custom')" variant="success">Add custom blend</b-btn>


      <!--   <h3>Add substances</h3>

        <h5>Filter Groups</h5>

        <multiselect @input="prepareSubstances" :multiple="true"  v-model="selected_groups.selected" :options="selected_groups.options"></multiselect>
        <hr>
        <multiselect class="mb-2" label="text" track-by="text" placeholder="Select substance" v-model="selected_substance.selected" @change="updateGroup($event)" :options="selected_substance.options"></multiselect>
      -->

    </div>
  </div>
</template>

<script>

import Multiselect from 'vue-multiselect'

export default {

  props: {
    substances: null,
    section: null,
    blends: null,
    countryOptions: null,
  },

  components: {
    Multiselect 
  },

  mounted(){
    this.prepareBlends()
  },

  data() {
    return {
      selected_countries: {
        selected: null,
        options: this.countryOptions,
      },

      new_blend: null,


      selected_substance: {
        selected: null,
        group: null,
        options: [],
      },

      selected_blends: {
        selected: null,
        options: [],
        substance_options: [],
      },

      group_field: {
        label: 'Blend',
        name: 'blend',
        expand: false,
        substance: null,
      },
    }
  },

  methods: {

    prepareSubstances(){
      this.selected_substance.options = []
      for(let group of this.substances) {
          for(let substance of group.substances){
            this.selected_substance.options.push({value: substance, text: substance, group: group})
            this.selected_blends.substance_options.push({value: substance, text: substance, group: group})
          }
      }
    },

    addNewBlend(){
      this.selected_blends.selected = null
      this.new_blend = {
        "name": null,
        substance_options: this.selected_blends.substance_options,
        "composition": [
          {
            "name": null,
            "percent": null,
          },
          {
            "name": null,
            "percent": null
          },
        ]
      }
    },

    removeSubstanceFromBlend(substance) {
      this.new_blend.composition.splice(this.new_blend.composition.indexOf(substance), 1)
    },

    addSubstanceToBlend(){
      this.new_blend.composition.push({name:null, percent: null})
    },

    prepareBlends(){
        for(let blend of this.blends) {
          this.selected_blends.options.push(blend)
        }
      this.prepareSubstances()
    },



    addSubstance(type) {
      if(type === 'selected') {
        for(let blend of this.selected_blends.selected) {
          let substance_fields = {
            get label () { return this.selected.name} ,
            name: this.removeSpecialChars(blend.name),
            substance_options: this.selected_blends.substance_options,
            selected: blend,
            comments: [{
                name: "party_remarks",
                label: "Remarks (party)",
                selected: '',
                type: "text",
              },
              {
                name: "sectretariat_comments",
                selected: '',
                type: "text",
                label: "Comments (Secretariat)",
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
              type: 'text',
              selected: null,
            },
            {
              label: 'Total Quantity Exported for All Uses',
              name: 'total_import_quantity_all_uses_recovered',
              description: 'Recovered and Reclaimed',
              disabled: false,
              type: 'text',
              selected: null,
            },
            {
              label: 'Quantity of New Substances Exported as Feedstock',
              name: 'import_quantity_new_substances_as_feedstock',
              description: '',
              disabled: false,
              type: 'text',
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
                      selected: null,
                      type: "text",
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
                      selected: null,
                      type: "text",
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
                      selected: null,
                      type: "text",
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
                      name: "quantity_in_metric",
                      selected: null,
                      type: "text",
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
                      name: "quantity_in_metric",
                      selected: null,
                      type: "text",
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
                      name: "quantity_in_metric",
                      selected: null,
                      type: "text",
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
            label: 'Blend',
            name: 'blend',
            expand: false,
            substance: null,
          }
        }
      } else {
            // let current_substances;
            for(let subst of this.new_blend.composition){
              subst.name = subst.name.value
            }

            let substance_fields = {
            get label () { return this.selected.name} ,
            name: this.removeSpecialChars(this.new_blend.name),
            substance_options: this.selected_blends.substance_options,
            // options: this.selected_substance.options,
            selected: this.new_blend,
            comments: [{
                name: "party_remarks",
                label: "Remarks (party)",
                selected: '',
                type: "text",
              },
              {
                name: "sectretariat_comments",
                selected: '',
                type: "text",
                label: "Comments (Secretariat)",
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
              type: 'text',
              selected: null,
            },
            {
              label: 'Total Quantity Exported for All Uses',
              name: 'total_import_quantity_all_uses_recovered',
              description: 'Recovered and Reclaimed',
              disabled: false,
              type: 'text',
              selected: null,
            },
            {
              label: 'Quantity of New Substances Exported as Feedstock',
              name: 'import_quantity_new_substances_as_feedstock',
              description: '',
              disabled: false,
              type: 'text',
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
                      selected: null,
                      type: "text",
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
                      selected: null,
                      type: "text",
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
                      selected: null,
                      type: "text",
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
                      name: "quantity_in_metric",
                      selected: null,
                      type: "text",
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
                      name: "quantity_in_metric",
                      selected: null,
                      type: "text",
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
                      name: "quantity_in_metric",
                      selected: null,
                      type: "text",
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
          this.group_field.custom = true
          var current_fields = this.section
          current_fields.push(this.group_field)
          this.section = current_fields

          this.group_field = {
            label: 'Blend',
            name: 'blend',
            expand: false,
            substance: null,
          }

      }

      this.resetData()
    },


    resetData() {

      this.selected_countries.selected = null

      this.group_field = {
        label: 'Blend',
        name: 'blend',
        expand: false,
        substance: null,
      }
    },

    removeSpecialChars(str) {
      return str.replace(/[^a-zA-Z0-9]+/g, "");
    },
  },

  watch: {
    blends: {
      handler: function(old_val, new_val) {
        this.prepareBlends()
      }
    }
  },

}
</script>

<style lang="css" scoped>

.add-blend-wrapper {
  white-space: nowrap; 
  margin-left: .5rem; 
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>