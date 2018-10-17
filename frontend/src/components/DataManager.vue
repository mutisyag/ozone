<template>
  <div>
    <tabsmanager v-if="countryOptions && substances && blends && current_submission && prefilled" :submission="current_submission" :data="{form: form, countryOptions: countryOptions, substances: substances, blends:blends}"></tabsmanager>
    <div v-else class="spinner">
      <div class="loader"></div>
    </div>
  </div>
</template>

<script>

import tabsManager from './TabsManager'
import form from '../assets/form.js'
import countryOptions from "@/assets/countryList.js"
import {getSubstances, getExportBlends, getParties, getSubmission} from '@/api/api.js'
import prefill from '@/mixins/prefill'
console.log(prefill)

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
      countryOptions: null,
      substances: null,
      blends: null,
      current_submission: null,
      prefilled: false,
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
    this.getSubstances()
    this.importCountries()
    getSubmission(this.submission).then( (response) => {
      this.current_submission = response.data
      this.prePrefill(form, this.current_submission)
    })
  },

  methods: {

    // ASYNC IMPORT IS SO SLOW
    // importCountries(){
    //   import('@/assets/countryList.js').then( (response ) => {
    //     let module = response.default
    //     module().then( exported => {
    //       this.countryOptions = exported
    //     })
    //   });
    // },

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

       console.log('toprefill',to_prefill)
      Object.keys(form.tabs).forEach( (tab) => {
       if(to_prefill.includes(this.fields_to_prefill[form.tabs[tab].name])) this.prefill(form.tabs[tab], data[this.fields_to_prefill[form.tabs[tab].name]])
      })
    },

    prefill(tab, data) {
      console.log('daatataaaaa', data)
      for(let entry of data) {
        this.prefillSubstance(entry, tab.form_fields)
      }

      console.log(tab.form_fields)
      this.prefilled = true
    },


    importCountries() {
      getParties().then(response => {
        let countryOptions = []
          for (let country of response.data) {
            countryOptions.push({ value: country.id, text: country.name})
          }
          this.countryOptions = countryOptions
      })
    },

    getSubstances(){
        getSubstances().then((response) => {
          this.substances = response.data 
          getExportBlends().then((response) => {
            this.blends = response.data
          })
        })
      }
  },
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