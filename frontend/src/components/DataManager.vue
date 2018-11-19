<template>
  <div>
    <tabsmanager v-if="initialDataReady" 
    :submission="current_submission" 
    :data="{form: form, countryOptions: initialData.countryOptions, substances: initialData.substances, blends: initialData.blends, display: initialData.display}"></tabsmanager>
    <div v-else class="spinner">
      <div class="loader"></div>
    </div>
  </div>
</template>

<script>

import tabsManager from './TabsManager'
import {fetch,getSubstances, getExportBlends, getParties, getSubmission, getCustomBlends} from '@/api/api.js'
import dummyTransition from '@/assets/dummyTransition.js'

export default {
  name: 'DataManager',
  components: {
    tabsmanager:tabsManager
  },


  props: {
    submission: String,
  },

  data () {
    return {
      form: this.$store.state.form,
      current_submission: null,
      prefilled: false,
      initialData: {
        countryOptions: null,
        substances: null,
        blends: null,
        display: {
          substances: {},
          blends: {},
          countries: {},
        }
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

  computed: {
    initialDataReady(){
      return  this.initialData.countryOptions 
              && this.initialData.substances 
              && this.initialData.blends 
              && this.current_submission 
              && this.initialData.display.substances 
              && this.initialData.display.blends 
              && this.initialData.display.countries
              && this.prefilled
    }
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
          this.$store.dispatch('prefillQuestionaire', this.current_submission.article7questionnaire)
        }
        
        this.$store.commit('updateFormPermissions', dummyTransition)
        this.prePrefill(this.form, this.current_submission)
      })
  },

   getCountries() {
    let countryOptions = []
    let countryDisplay = {}
    getParties().then(response => {
          for (let country of response.data) {
            countryOptions.push({ value: country.id, text: country.name})
            countryDisplay[country.id] = country.name
          }
      this.initialData.display.countries = countryDisplay
      this.initialData.countryOptions = countryOptions
    })
  },

  getSubstances(){
    let tempSubstances = []
    let substancesDisplay = {}
        getSubstances().then((response) => {
          for(let group of response.data) {
              for(let substance of group.substances){
                tempSubstances.push({value: substance.id, text: substance.name, group: group})
                substancesDisplay[substance.id] = substance.name
              }
          }
          this.initialData.display.substances = substancesDisplay
          this.initialData.substances = tempSubstances 
        })
  },

    getCustomBlends(){
      let blendsDisplay = {}
      getCustomBlends().then((response) => {
        for(let blend of response.data) {
          blendsDisplay[blend.id] = {name: blend.blend_id, components: blend.components}
        }
        this.initialData.display.blends = blendsDisplay
        this.initialData.blends = response.data
      })
    },

    prePrefill(form, prefill_data) {
        Object.keys(form.tabs).forEach( (tab) => {
          if(this.fields_to_get[tab]){
            fetch(prefill_data[this.fields_to_get[tab]]).then( response => {
              if(response.data.length) {
                this.$store.commit('setTabStatus',{tab:tab, value:'saving'})
                this.$nextTick(() => {
                  setTimeout(() => {
                    this.prefill(form.tabs[tab], JSON.parse(JSON.stringify(response.data)))
                  },100)
                })
              } else {
                this.$store.commit('updateNewTabs', tab)
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
            this.$store.dispatch('createSubstance',{
             substanceList: item.substance ? [item.substance] : null,
             currentSectionName: tab.name, 
             groupName: null, 
             country: null, 
             blendList: item.blend ? [item.blend] : null, 
             prefillData: item
            })
          }
        }
      } else {
          data.forEach( el => this.$store.dispatch('prefillEmissionsRow', el))
         }
          this.$nextTick(() => {
            setTimeout(() => {
                this.$store.commit('setTabStatus',{tab: tab.name, value:true})
            })
          })
    },

   

  },


  watch: {
     initialData: {
         handler(val){
            if(val.blends && val.countryOptions && val.substances && val.display.substances && val.display.blends && val.display.countries) {
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