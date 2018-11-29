<template>
    <b-btn @click="validation" style="border-top-right-radius: 0;border-bottom-right-radius:0" variant="outline-success">
        Save
      </b-btn>
</template>

<script>

import {post, fetch, update} from '@/api/api'

export default {

  name: 'Save',

  data () {
    return {
        invalidTabs: [],
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
              'remarks_party': '',
              'remarks_os': '',
              'quantity_total_new': null,
              'quantity_total_recovered': null,
              'quantity_feedstock': null,
              'quantity_critical_uses': null,
              'decision_critical_uses': '',
              'quantity_essential_uses': null,
              'decision_essential_uses': '',
              'quantity_high_ambient_temperature': null,
              'decision_high_ambient_temperature': '',
              'quantity_laboratory_analytical_uses': null,
              'decision_laboratory_analytical_uses': '',
              'quantity_process_agent_uses': null,
              'decision_process_agent_uses': '',
              'quantity_quarantine_pre_shipment': null,
              'decision_quarantine_pre_shipment': '',
              'destination_party': null,
              'substance': null,
              'blend': null,
              'decision': null
            },
          'has_imports' : {
              'remarks_party': '',
              'remarks_os': '',
              'quantity_total_new': null,
              'quantity_total_recovered': null,
              'quantity_feedstock': null,
              'quantity_critical_uses': null,
              'decision_critical_uses': '',
              'quantity_essential_uses': null,
              'decision_essential_uses': '',
              'quantity_high_ambient_temperature': null,
              'decision_high_ambient_temperature': '',
              'quantity_laboratory_analytical_uses': null,
              'decision_laboratory_analytical_uses': '',
              'quantity_process_agent_uses': null,
              'decision_process_agent_uses': '',
              'quantity_quarantine_pre_shipment': null,
              'decision_quarantine_pre_shipment': '',
              'source_party': null,
              'substance': null,
              'blend': null,
              'decision': null
            },
          'has_produced' : {
              'remarks_party': '',
              'remarks_os': '',
              'quantity_critical_uses': null,
              'decision_critical_uses': '',
              'quantity_essential_uses': null,
              'decision_essential_uses': '',
              'quantity_high_ambient_temperature': null,
              'decision_high_ambient_temperature': '',
              'quantity_laboratory_analytical_uses': null,
              'decision_laboratory_analytical_uses': '',
              'quantity_process_agent_uses': null,
              'decision_process_agent_uses': '',
              'quantity_quarantine_pre_shipment': null,
              'decision_quarantine_pre_shipment': '',
              'quantity_total_produced': null,
              'quantity_feedstock': null,
              'quantity_article_5': null,
              'substance': null
          },
          'has_destroyed' : {
              'remarks_party': '',
              'remarks_os': '',
              'quantity_destroyed': null,
              'substance': null,
              'blend': null
          },
          'has_nonparty' : {
              'remarks_party': '',
              'remarks_os': '',
              'quantity_import_new': null,
              'quantity_import_recovered': null,
              'quantity_export_new': null,
              'quantity_export_recovered': null,
              'substance': null,
              'blend': null,
              'trade_party': null
          },
          'questionaire_questions': {
              'remarks_party': '',
              'remarks_os': '',
              'has_imports': false,
              'has_exports': false,
              'has_produced': false,
              'has_destroyed': false,
              'has_nonparty': false,
              'has_emissions': false
          },
          'has_emissions' :{
              'remarks_party': '',
              'remarks_os': '',
              'facility_name': '',
              'quantity_generated': null,
              'quantity_feedstock': null,
              'quantity_destroyed': null,
              'quantity_emitted': null
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
      let tabsToValidate = ['has_imports','has_exports','has_produced','has_destroyed','has_nonparty','has_emissions']
      for(let tab of tabsToValidate){
        for(let field of this.$store.state.form.tabs[tab].form_fields){
          if(field.validation.selected.length){
            this.invalidTabs.push(this.$store.state.form.tabs[tab].name)
            this.$store.commit('setTabStatus', {tab: tab, value: false})
            break;
          }
        }
      }
      this.startSubmitting()
    },


  	startSubmitting(){
      this.submitQuestionaireData('questionaire_questions')
      for(let questionnaire_field of Object.values(this.$store.state.form.tabs.questionaire_questions.form_fields)) {
        if(questionnaire_field.selected && !this.invalidTabs.includes(questionnaire_field.name)) {
            this.submitData(questionnaire_field.name)
        } else if (!questionnaire_field.selected && this.$store.state.form.tabs[questionnaire_field.name].form_fields.length){
            this.$store.dispatch('removeDataFromTab',questionnaire_field.name).then( r => {
              this.submitData(questionnaire_field.name)
            })
        }
      }
  	},

    submitQuestionaireData(field) {
       const current_tab = Object.values(this.$store.state.form.tabs).find( (value) => { return value.name === field} )
       let save_obj = JSON.parse(JSON.stringify(this.form_fields[field]))
       Object.values(current_tab.form_fields).forEach( form_field => {
        save_obj[form_field.name]  = form_field.selected
       })

      post(this.$store.state.current_submission[this.fields_to_save[field]], save_obj).then( (response) => {
        }).catch((error) => {
        console.log(error)
      })
    },  

    submitData(field) {
       const current_tab = this.$store.state.form.tabs[field]
       if(this.$store.state.newTabs.indexOf(field) === -1){
       current_tab.status = 'saving'
       let current_tab_data = []
         current_tab.form_fields.forEach( form_field => {
          let save_obj = JSON.parse(JSON.stringify(this.form_fields[field]))
          
          for(let field in form_field) {
            save_obj[field] = form_field[field].selected
          }

           current_tab_data.push(save_obj)
         })

        update(this.$store.state.current_submission[this.fields_to_save[field]], current_tab_data).then( (response) => {
              current_tab.status = true
              if(current_tab_data.length){
                this.$store.commit('tabHasBeenSaved', field)
              } else {
                this.$store.commit('updateNewTabs', field)
              }
              }).catch((error) => {
              current_tab.status = false
              console.log(error.response)
              this.invalidTabs.push(field)
              this.$store.dispatch('setAlert', { message:  `Save failed for ${this.invalidTabs}`, variant: 'danger' })
            })

       } else if (this.$store.state.newTabs.indexOf(field) !== -1 && current_tab.form_fields.length) {

       current_tab.status = 'saving'
       
       let current_tab_data = []

         current_tab.form_fields.forEach( form_field => {
          let save_obj = JSON.parse(JSON.stringify(this.form_fields[field]))
          
          for(let field in form_field) {
            save_obj[field] = form_field[field].selected
          }

           current_tab_data.push(save_obj)
         })

        post(this.$store.state.current_submission[this.fields_to_save[field]], current_tab_data).then( (response) => {
              current_tab.status = true
              this.$store.commit('tabHasBeenSaved', field)
              }).catch((error) => {
              current_tab.status = false
              this.invalidTabs.push(field)
              this.$store.dispatch('setAlert', { message:  `Save failed for ${this.invalidTabs}`, variant: 'danger' })
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