<template>
  <div v-if="section && field && inner_field && countryOptions">
    <div class="container">
      <div style="position: relative">
          <multiselect :max-height="250" :multiple="true" :clear-on-select="false" :hide-selected="true" :close-on-select="false" label="text" track-by="value" placeholder="Countries" v-model="selected_countries.selected" :options="this.current_field.substance.inner_fields[0].options"></multiselect>
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
    recomputeCountries: null,
    countryOptions: Array,
  },

  components: {
    Multiselect 
  },

  created(){
    this.field = JSON.parse(JSON.stringify(this.current_field))
  },

  computed:{
    watchParent: {
       get: function(){
        return JSON.parse(JSON.stringify(this.$parent.$children.length))
      }
    }
  },

  mounted(){
    this.prepareCountries();
  },

  data() {
    return {
      substances: null,
      field: null,
      existing_countries: {},
      selected_countries: {
        selected: null,
      },
    }
  },


  destroyed() {
      this.$emit('update:recomputeCountries', this.recomputeCountries + 1)
  },

  methods: {

    prepareCountries(){
      console.log('preparing countries')

      this.section.form_fields.forEach( field => {
        let substance_key = field.substance.selected.value || field.substance.selected.id
        console.log('substance_key', substance_key)
        if(!this.existing_countries[substance_key]) {
          this.$set(this.existing_countries, substance_key, [])
        }
        field.substance.inner_fields.forEach( inner_field => {
          if(['source_party', 'destination_party', 'trade_party'].includes(inner_field.name) && inner_field.selected) {
              this.pushUnique(this.existing_countries[substance_key],inner_field.selected.value)
          } 
        })

         field.substance.inner_fields.forEach( inner_field => {
           if (['source_party', 'destination_party', 'trade_party'].includes(inner_field.name) && !inner_field.selected) {
            this.existing_countries[substance_key].forEach( country => {
              let to_remove = inner_field.options.find( (country_values) => {
                return country_values.value === country
              })
              inner_field.options.splice(inner_field.options.indexOf(to_remove), 1)
              
            })
          }
        })
      });
    },

    pushUnique(array, item) {
      if (array.indexOf(item) === -1) {
        array.push(item);
      }
    },


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


  watch: {
    recomputeCountries: function(newVal, oldVal){
      this.resetData()
      this.prepareCountries()
    },
    existing_countries: {
      handler: function(newVal, oldVal) {
        this.prepareCountries()
      },
      deep: true
    }
  }

}
</script>

<style lang="css" scoped>
</style>