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

import createSubstance from '@/mixins/createSubstance.vue'


export default {
  name: 'DataManager',
  components: {
    tabsmanager:tabsManager
  },

  mixins: [
    prefill, createSubstance
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
          // 'questionaire_questions' : 'article7questionnaire_url',
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
      if(!this.submission) {
        this.$router.push({ name: 'Dashboard' });
      }

      getSubmission(this.submission).then( (response) => {
        this.current_submission = response.data
        if(this.current_submission.article7questionnaire){
          this.prefillQuestionaire(this.form, this.current_submission.article7questionnaire)
        }
        
        this.prePrefill(this.form, this.current_submission)
        // this.prefilled = true
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
                form.tabs[tab].status = 'saving'
                this.$nextTick(() => {
                  setTimeout(() => {
                    this.prefill(form.tabs[tab], JSON.parse(JSON.stringify(response.data)))
                  },100)
                })
              }
            }).catch( error => {
              console.log(error)
            })
          }
        })
        this.prefilled = true
    },

    prefill(tab, data) {

      if(tab.name != 'has_emissions'){

        if(data) {
          for(let item of data) {
            // substanceList, currentSectionName, groupName, currentSection, country, blend, prefillData
            this.createSubstance([item.substance], tab.name, null, tab.form_fields, null, [item.blend], item)
          }
        }
      } else {

            for(let item of data) {
              let row = {
                  id: {
                    selected: null,
                  },
                  facility_name: {
                        type: 'text',
                        selected: '',
                    },
                  quantity_generated: {
                        type: 'number',    
                        selected: '',
                    },
                   quantity_feedstock: {
                        type: 'number',
                        selected: '',
                    },
                   quantity_destroyed: {
                        type: 'number',
                        selected: '',
                    },
                   quantity_emitted: {
                        type: 'number',
                        selected: '',
                    },
                    remarks_party: {
                     type: 'textarea',
                       selected: '',
                    },
                    remarks_os: {
                       type: 'textarea',
                       selected: '',
                    },
                    get validation() {
                     let errors = []
                     if(!this.facility_name.selected){
                        errors.push('eroare1')
                     }

                     let returnObj = {
                        type: 'nonInput',
                        selected: errors
                     }

                     return returnObj
                  },
              }

              for(let field in item) {
                console.log(field)
                row[field].selected = item[field]
              }

              tab.form_fields.push(row)
            }
         }
        this.$nextTick(() => {
            setTimeout(() => {
              tab.status = true
            })
          })



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