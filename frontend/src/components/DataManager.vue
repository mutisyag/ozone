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
import prefillSubstance from '@/mixins/prefill.js'
import {getSubstances, getExportBlends, getParties, getSubmission} from '@/api/api.js'


export default {
  name: 'DataManager',
  components: {
    tabsmanager:tabsManager
  },

  // mixins: [
  //   prefill
  // ],

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
          'import_question' : 'article7imports_url',
          'export_question' : 'article7exports',
          'production_question' : 'article7productions_url',
          'destruction_question' : 'article7destructions_url',
          'nonparty_question' : 'article7nonpartytrades_url',
          'emissions_question' : 'article7emissions_url',
      },
    }
  },


  created() {
    this.getInitialData()
  },

  methods: {

  getInitialData(){
    this.getBlends();
    this.getCountries();
    this.getSubstances();
  },


  getCurrentSubmission(){
        getSubmission(this.submission).then( (response) => {
        this.current_submission = response.data
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
  getBlends(){
        getExportBlends().then((response) => {
          this.initialData.blends = response.data
        })
  },

    prePrefill(form, prefill_data) {
      let data = JSON.parse(JSON.stringify(prefill_data))
      let to_prefill = [];
       Object.keys(data).forEach( (key) => {
          if(typeof(data[key]) != 'object' || !data[key] || !data[key].length){
            delete data[key]
          } else {
            to_prefill.push(key)
          }
        })
      if(to_prefill.length){
        Object.keys(form.tabs).forEach( (tab) => {
         if(to_prefill.includes(this.fields_to_prefill[form.tabs[tab].name])) this.prefill(form.tabs[tab], data[this.fields_to_prefill[form.tabs[tab].name]],this.initialData.countryOptions)
        })
      } else {
        this.prefilled = true
      }
    },

    prefill(tab, data, countries) {
      for(let entry of data) {
        let current_substance = this.initialData.substances.find( val => val.text === entry.substance )
        let current_party = this.initialData.countryOptions.find( val => val.value === entry.destination_party)
        prefillSubstance(entry, tab.form_fields, countries, current_party, current_substance, this.initialData.substances)
      }

      this.prefilled = true
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