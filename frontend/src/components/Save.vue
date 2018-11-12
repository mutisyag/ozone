<template>
  <span>
    
    <b-btn @click="validation" style="border-top-right-radius: 0;border-bottom-right-radius:0" variant="outline-success">
        Save
      </b-btn>

       <b-alert variant="danger"
             dismissible
             style="position: fixed;
                top: 0;
                z-index: 10000;
                width: 100%;
                left: 0;
                right: 0;"
             :show="showDismissibleAlert"
             @dismissed="showDismissibleAlert=false"
             >
             <div v-if="current_duplicates" v-html="current_duplicates"></div>
             <div v-if="errorMessage" v-html="errorMessage"></div>
      </b-alert>

  </span>

</template>

<script>

import {post, fetch} from '@/api/api'
export default {

  name: 'Save',

  props:{
  	data: Object,
  	submission: Object,
  },

  data () {
    return {
        findDuplicates: {},
        showDismissibleAlert: false,
        showDismissibleAlertSave: false,
        current_duplicates: '',
        invalidTabs: [],
        errorMessage: null,
        duplicatesFound: [],
        fields_to_save: {
          'questionaire_questions' : 'article7questionnaire_url',
          'has_imports' : 'article7imports_url',
          'has_exports' : 'article7exports_url',
          'has_produced' : 'article7productions_url',
          'has_destroyed' : 'article7destructions_url',
          'has_nonparty' : 'article7nonpartytrades_url',
          'has_emissions' : 'article7emissions_url',
        },
        form_fields: {
          'has_exports' : {
              "remarks_party": "",
              "remarks_os": "",
              "quantity_total_new": null,
              "quantity_total_recovered": null,
              "quantity_feedstock": null,
              "quantity_critical_uses": null,
              "decision_critical_uses": "",
              "quantity_essential_uses": null,
              "decision_essential_uses": "",
              "quantity_high_ambient_temperature": null,
              "decision_high_ambient_temperature": "",
              "quantity_laboratory_analytical_uses": null,
              "decision_laboratory_analytical_uses": "",
              "quantity_process_agent_uses": null,
              "decision_process_agent_uses": "",
              "quantity_quarantine_pre_shipment": null,
              "decision_quarantine_pre_shipment": "",
              "destination_party": null,
              "substance": null,
              "blend": null,
              "decision": null
            },
          'has_imports' : {
              "remarks_party": "",
              "remarks_os": "",
              "quantity_total_new": null,
              "quantity_total_recovered": null,
              "quantity_feedstock": null,
              "quantity_critical_uses": null,
              "decision_critical_uses": "",
              "quantity_essential_uses": null,
              "decision_essential_uses": "",
              "quantity_high_ambient_temperature": null,
              "decision_high_ambient_temperature": "",
              "quantity_laboratory_analytical_uses": null,
              "decision_laboratory_analytical_uses": "",
              "quantity_process_agent_uses": null,
              "decision_process_agent_uses": "",
              "quantity_quarantine_pre_shipment": null,
              "decision_quarantine_pre_shipment": "",
              "source_party": null,
              "substance": null,
              "blend": null,
              "decision": null
            },
          'has_produced' : {
              "remarks_party": "",
              "remarks_os": "",
              "quantity_critical_uses": null,
              "decision_critical_uses": "",
              "quantity_essential_uses": null,
              "decision_essential_uses": "",
              "quantity_high_ambient_temperature": null,
              "decision_high_ambient_temperature": "",
              "quantity_laboratory_analytical_uses": null,
              "decision_laboratory_analytical_uses": "",
              "quantity_process_agent_uses": null,
              "decision_process_agent_uses": "",
              "quantity_quarantine_pre_shipment": null,
              "decision_quarantine_pre_shipment": "",
              "quantity_total_produced": null,
              "quantity_feedstock": null,
              "quantity_article_5": null,
              "substance": null
          },
          'has_destroyed' : {
              "remarks_party": "",
              "remarks_os": "",
              "quantity_destroyed": null,
              "substance": null,
              "blend": null
          },
          'has_nonparty' : {
              "remarks_party": "",
              "remarks_os": "",
              "quantity_import_new": null,
              "quantity_import_recovered": null,
              "quantity_export_new": null,
              "quantity_export_recovered": null,
              "substance": null,
              "blend": null,
              "trade_party": null
          },
          'questionaire_questions': {
              "remarks_party": "",
              "remarks_os": "",
              "has_imports": false,
              "has_exports": false,
              "has_produced": false,
              "has_destroyed": false,
              "has_nonparty": false,
              "has_emissions": false
          },
          'has_emissions' :{
              "remarks_party": "",
              "remarks_os": "",
              "facility_name": "",
              "quantity_generated": null,
              "quantity_feedstock": null,
              "quantity_destroyed": null,
              "quantity_emitted": null
          }
        },
    }
  },
  methods:{
    pushUnique(array, item) {
      if (array.indexOf(item) === -1) {
        array.push(item);
      }
    },



    validation(){
      this.invalidTabs = []
      let tabsToValidate = ['tab_2','tab_3','tab_4','tab_5','tab_6','tab_7',]
      for(let tab of tabsToValidate){
        for(let field of this.data.tabs[tab].form_fields){
          console.log(field)
          if(field.validation.selected.length){
            this.invalidTabs.push(this.data.tabs[tab].name)
            this.data.tabs[tab].status = false
            break;
          }
        }
      }
      
      this.startSubmitting()
      
    },


  	startSubmitting(){
      this.errorMessage = null
      this.current_duplicates = null
      this.submitQuestionaireData('questionaire_questions')
      for(let questionnaire_field of this.data.tabs.tab_1.form_fields) {
        if(questionnaire_field.selected && !this.invalidTabs.includes(questionnaire_field.name)) {
            this.submitData(questionnaire_field.name)
        }
      }
  	},

    submitQuestionaireData(field) {
       const current_tab = Object.values(this.data.tabs).find( (value) => { return value.name === field} )
       let save_obj = JSON.parse(JSON.stringify(this.form_fields[field]))
       current_tab.form_fields.forEach( form_field => {
        save_obj[form_field.name]  = form_field.selected
       })

      post(this.submission[this.fields_to_save[field]], save_obj).then( (response) => {
        console.log(response)
        }).catch((error) => {
        console.log('here',error)
      })
    },  

    submitData(field) {
       const current_tab = Object.values(this.data.tabs).find( (value) => { return value.name === field} )
       if(current_tab.form_fields.length){
      
       current_tab.status = 'saving'
       
       let current_tab_data = []

       if(field === 'has_emissions') {
        current_tab.form_fields.forEach( form_field => {
          let current_field = form_field 
          let save_obj = JSON.parse(JSON.stringify(this.form_fields[field]))
            
          current_field.forEach( inner_field => {
             save_obj[inner_field.name] = inner_field.selected 
          })

           current_tab_data.push(save_obj)
         })
 
       } else {

         current_tab.form_fields.forEach( form_field => {
          let save_obj = JSON.parse(JSON.stringify(this.form_fields[field]))
          
          for(let field in form_field) {
            save_obj[field] = form_field[field].selected
          }

           current_tab_data.push(save_obj)
         })
       }

        post(this.submission[this.fields_to_save[field]], current_tab_data).then( (response) => {
              this.showDismissibleAlertSave = true
              current_tab.status = true
              }).catch((error) => {
              current_tab.status = false
              console.log(error.response)
            })

       }


    },
  }
}
</script>

<style lang="css" scoped>

.alert b {
  margin-right: 1rem;
}

</style>