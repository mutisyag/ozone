<template>
  <div>
    <tabsmanager v-if="initialData.countryOptions && initialData.substances && initialData.blends && current_submission && prefilled" :submission="current_submission" :data="{form: form, countryOptions: initialData.countryOptions, substances: initialData.substances, blends: initialData.blends}"></tabsmanager>
    <div v-else class="spinner">
      <div class="loader"></div>
    </div>
  </div>
</template>

<script>

import tabsManager from './TabsManager'
import form from '../assets/form.js'
import prefill from '@/mixins/prefill'
import {fetch,getSubstances, getExportBlends, getParties, getSubmission, getCustomBlends} from '@/api/api.js'


export default {
  name: 'DataManager',
  components: {
    tabsmanager:tabsManager
  },

  mixins: [
    prefill
  ],

  props: {
    submission: String,
  },

  data () {
    return {
      form: JSON.parse(JSON.stringify(form)),
      current_submission: null,
      prefilled: false,
      initialData: {
        countryOptions: null,
        substances: null,
        blends: null,
      },
      fields_to_prefill: {
          'questionaire_questions' : 'article7questionnaire',
          'has_imports' : 'article7imports',
          'has_exports' : 'article7exports',
          'has_produced' : 'article7productions',
          'has_destroyed' : 'article7destructions',
          'has_nonparty' : 'article7nonpartytrades',
          'has_emissions' : 'article7emissions',
      },
      fields_to_get: {
          'questionaire_questions' : 'article7questionnaire_url',
          'has_imports' : 'article7imports_url',
          'has_exports' : 'article7exports_url',
          'has_produced' : 'article7productions_url',
          'has_destroyed' : 'article7destructions_url',
          'has_nonparty' : 'article7nonpartytrades_url',
          'has_emissions' : 'article7emissions_url',
      },
    }
  },


  created() {
    this.getInitialData()
  },

  methods: {

  getInitialData(){
    this.getCountries();
    this.getSubstances();
    this.getCustomBlends();
  },


  getCurrentSubmission(){
      getSubmission(this.submission).then( (response) => {
        this.current_submission = response.data
        if(this.current_submission.article7questionnaire){
          this.prefillQuestionaire(this.form, this.current_submission.article7questionnaire)
        }
        
        this.prePrefill(this.form, this.current_submission)
      })
  },

   getCountries() {
    let countryOptions = []
    getParties().then(response => {
          for (let country of response.data) {
            countryOptions.push({ value: country.id, text: country.name})
          }
      this.initialData.countryOptions = countryOptions
    })
  },

  getSubstances(){
    let tempSubstances = []
        getSubstances().then((response) => {
          for(let group of response.data) {
              for(let substance of group.substances){
                tempSubstances.push({value: substance.id, text: substance.name, group: group})
              }
          }
          this.initialData.substances = tempSubstances 
        })
  },

    getCustomBlends(){
      getCustomBlends().then((response) => {
        this.initialData.blends = response.data
      })
    },

    prePrefill(form, prefill_data) {
      
        Object.keys(form.tabs).forEach( (tab) => {
          if(this.fields_to_get[form.tabs[tab].name]){
            
            fetch(prefill_data[this.fields_to_get[form.tabs[tab].name]]).then( response => {
              if(response.data.length) {
                this.prefill(form.tabs[tab], JSON.parse(JSON.stringify(response.data)),this.initialData.countryOptions)
              }
            }).catch( error => {
              console.log(error.response)
            })
          }
        })
    },

    prefill(tab, data, countries) {
      for(let entry of data) {
        let current_substance = entry.substance 
        ? 
          this.initialData.substances.find( val => val.value === entry.substance ) 
        : 
          this.initialData.blends.find( val => val.id === entry.blend )

        let current_party = this.initialData.countryOptions.find( val => val.value === entry.destination_party || val.value === entry.source_party)
        this.prefillSubstance(tab.name, entry, tab.form_fields, countries, current_party, current_substance, this.initialData.substances, this.initialData.blends)
      }

      this.prefilled = true
    },

    prefillQuestionaire(form,data){
      for(let questionaire_question in data) {
       let current_field = this.form.tabs.tab_1.form_fields.find( field =>  field.name === questionaire_question )

       // TODO: investigate. The if shouldn't be needed
       if(current_field){
        current_field.selected = data[questionaire_question]
       }
      }
    },

  },


  watch: {
     initialData: {
         handler(val){
            if(val.blends && val.countryOptions && val.substances) {
              this.getCurrentSubmission()
            }
         },
         deep: true
      }
    }

}
</script>

<style lang="css" scoped>

.spinner {
    z-index: 1;
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(0,0,0,0.2);
    display: flex;
    justify-content: center;
    align-items: center;
}

.loader {
  border: 16px solid #f3f3f3;
  border-radius: 50%;
   border-top: 16px solid blue;
   border-right: 16px solid green;
   border-bottom: 16px solid red;
   border-left: 16px solid pink;
  width: 120px;
  height: 120px;
  -webkit-animation: spin 2s linear infinite; /* Safari */
  animation: spin 2s linear infinite;
}

/* Safari */
@-webkit-keyframes spin {
  0% { -webkit-transform: rotate(0deg); }
  100% { -webkit-transform: rotate(360deg); }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>