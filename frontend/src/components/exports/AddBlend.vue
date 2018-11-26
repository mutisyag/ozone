<template>
  <div>
    <div class="container">

     
        <div class="mt-2 mb-2" style="display: flex;">
          <multiselect trackBy="value"  :clear-on-select="false" :hide-selected="true" :close-on-select="false" :multiple="true" label="text" v-model="selected_blends.selected" @input="new_blend = null" placeholder="Select predefined blend" :options="selected_blends.options"></multiselect>
          <div class="add-blend-wrapper"><b>/</b> <b-btn style="margin-left: .5rem" variant="primary" @click="addNewBlend">Add new blend</b-btn></div>
        </div>


        <div :key="blend.name" v-if="selected_blends.selected" v-for="blend in selected_blends.selected">
          <h5>Composition of <b>{{display.blends[blend].name}}</b></h5>
          <b-row v-for="substance in display.blends[blend].components">
            <b-col>{{substance.component_name}}</b-col>
            <b-col>{{substance.percentage.toLocaleString("en", {style: "percent"})}}</b-col>
          </b-row>
        </div>
      
       <div v-if="new_blend">
          <h5>Composition</h5>
          <b-input-group prepend="Blend name">
            <b-form-input type="text" @blur.native="alertIfBlendExists" v-model="new_blend.text"></b-form-input>
            <b-input-group-append>
              <b-btn variant="default" @click="addSubstanceToBlend">+</b-btn>
            </b-input-group-append>
          </b-input-group>
          <b-input-group class="mb-2 mt-2" v-for="substance in new_blend.composition">
              <b-input-group-prepend>
                <b-btn  style="z-index:initial;"  variant="danger" @click="removeSubstanceFromBlend(substance)">X</b-btn>
              </b-input-group-prepend>
              <multiselect label="text"  @tag="addTag($event,substance)" :taggable="true" trackBy="value" placeholder="Substance" v-model="substance.name" :options="substances"></multiselect>
              <b-input-group-append>
                <b-form-input type="text" placeholder="%" v-model="substance.percent"></b-form-input>
              </b-input-group-append>
          </b-input-group>
          <small>Note: If a non standard blend not listed in section 11 of the data reporting instructions and guidelines is to be reported, please indicate the percentage by weight of each constituent controlled substance of the mixture being reported in the “comments” box above.</small>
        </div>

      <hr>
      <b-btn v-if="selected_blends.selected" @click="addSubstance('selected')" variant="success">Add selected blends</b-btn>
      <b-btn v-if="new_blend" :disabled="!blendIsValid" @click="addSubstance('custom')" variant="success">Add custom blend</b-btn>


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

import {createBlend} from '@/api/api'
import Multiselect from '@/mixins/modifiedMultiselect'



export default {

  props: {
    // blends: null,
    // countryOptions: null,
    // display: null,
    tabName: String,
  },
  
  computed: {
    substances(){
      return JSON.parse(JSON.stringify(this.$store.state.initialData.substances))
    },
    blends(){
      return this.$store.state.initialData.blends
    },

    display(){
      return this.$store.state.initialData.display
    },

    blendIsValid(){
      return !this.$store.getters.checkIfBlendAlreadyEists(this.new_blend.text) && this.new_blend.composition.every((substance) => {return substance.name && substance.percent})
    },
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

      submit_blend: {
        components: null,
        blend_id: null,
        type: "Zeotrope"
      },

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

    }
  },

  methods: {

    addTag (newTag, substance) {
      console.log(newTag,substance)
        const tag = {
          text: newTag,
          value: newTag
        }
        this.substances.push(tag)
        substance.name = newTag
    },

    prepareSubstances(){
      this.selected_substance.options = []
      for(let substance of this.substances) {
            this.selected_substance.options.push({value: substance.id, text: substance.name, group: substance.group})
      }
    },

    alertIfBlendExists(){
      console.log('here')
      if(this.$store.getters.checkIfBlendAlreadyEists(this.new_blend.text)) { 
          this.$store.dispatch('setAlert', { message:  `A blend with the name ${this.new_blend.text} already exists!`, variant: 'danger' })
      }

    },

    addNewBlend(){
      this.selected_blends.selected = null
      this.new_blend = {
        "text": null,
        "value": null,
        "composition": [
          {
            "name": null,
            "percent": null,
          },
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
          this.selected_blends.options.push({text: blend.blend_id, value: blend.id})
        }
      this.prepareSubstances()
    },



    addSubstance(type) {
      if(type === 'selected') {
      this.$store.dispatch('createSubstance',{
         substanceList: null,
         currentSectionName: this.tabName, 
         groupName: null, 
         country: null, 
         blendList: this.selected_blends.selected, 
         prefillData: null
        })

      } else {
          
          this.submit_blend.blend_id = this.new_blend.text
          this.submit_blend.components = []
          this.submit_blend.party = this.$store.state.current_submission.party
          for(let substance of this.new_blend.composition) {
            if(typeof(substance.name) === 'string'){
              this.submit_blend.components.push({component_name: substance.name, substance: null, percentage: substance.percent/100})
            } else {
              this.submit_blend.components.push({component_name: null, substance: substance.name, percentage: substance.percent/100})
            }
          }
          console.log(this.submit_blend)
          createBlend(this.submit_blend).then(response =>  {
            console.log(response)
            this.new_blend.value = response.data.id

            this.$store.commit('addCreateBlendToBlendList', response.data)
            
            this.display.blends[response.data.id] = {name: response.data.blend_id, components: response.data.components}

             this.$store.dispatch('createSubstance',{
                   substanceList: null,
                   currentSectionName: this.tabName, 
                   groupName: null, 
                   country: null, 
                   blendList: [this.new_blend.value], 
                   prefillData: null
                  })

          }).catch((error) => {
                this.$store.dispatch('setAlert', { message:  error.response.data, variant: 'danger' })
          })

          console.log(this.new_blend)
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