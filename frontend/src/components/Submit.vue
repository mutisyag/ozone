<template>
	  <b-btn @click="startSubmitting" variant="success">
        Submit
      </b-btn>
</template>

<script>

import {post, fetch} from '@/api/api'
export default {

  name: 'Submit',

  props:{
  	data: Object,
  	submission: Object,
  },

  data () {
    return {
        fields_to_save: {
          'questionaire_questions' : 'article7questionnaire_url',
          'import_question' : 'article7imports_url',
          'export_question' : 'article7exports_url',
          'production_question' : 'article7productions_url',
          'destruction_question' : 'article7destructions_url',
          'nonparty_question' : 'article7nonpartytrades_url',
          'emissions_question' : 'article7emissions_url',
        },
        form_fields: {
          'export_question' : {
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
          'import_question' : {
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
              "source_party": 1,
              "substance": null,
              "blend": null,
              "decision": null
            },
          'production_question' : {
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
          'destruction_question' : {
              "remarks_party": "",
              "remarks_os": "",
              "quantity_destroyed": null,
              "substance": null,
              "blend": null
          },
        },
    }
  },
  methods:{
  	startSubmitting(){
  		console.log(this.data,this.submission)
      for(let questionnaire_field of this.data.tabs.tab_1.form_fields) {
        if(questionnaire_field.selected) {
            this.submitData(questionnaire_field.name)
        }
      }
  	},

    submitData(field) {
       const current_tab = Object.values(this.data.tabs).find( (value) => { return value.name === field} )
       console.log('------current_tab--------', field)
       // for some reason calling [0,1].forEach() in a certain iteration causes erros. Probably babel stuff
       let small_iterator = [0,1]
       let current_tab_data = []
       current_tab.form_fields.forEach( form_field => {
        let substance = form_field.substance 
        let save_obj = JSON.parse(JSON.stringify(this.form_fields[field]))
        console.log(save_obj)
        if(substance.comments) {
         small_iterator.forEach( i => save_obj[substance.comments[i].name] = substance.comments[i].selected )
        }
        
        substance.type != 'blend' ? save_obj['substance'] = substance.selected.value : save_obj['blend'] = substance.selected.id 
        
        substance.inner_fields.forEach( inner_field => {
          inner_field.type != 'multiple_fields' 
          ? 
          inner_field.type != 'select'  ? save_obj[inner_field.name]  = inner_field.selected : inner_field.selected ? save_obj[inner_field.name]  = inner_field.selected.value : save_obj[inner_field.name] = inner_field.selected 
          :
          inner_field.fields.forEach( inner_inner_field => {
            small_iterator.forEach( i => save_obj[inner_inner_field.fields[i].name] = inner_inner_field.fields[i].selected )
          })          
        })

         current_tab_data.push(save_obj)
       })
        
       post(this.submission[this.fields_to_save[field]], current_tab_data).then( (response) => {
        console.log(response)
        }).catch((error) => {
        console.log(this.$validator)
            this.$validator._base.validateAll().then((result) => {
              if (result) {
                // eslint-disable-next-line
                // console.log(result)
                alert('Form Submitted!');
                return;
              }

              

              alert('Correct erros');
            });

        console.log('here',error)
      })

    },
  }
}
</script>

<style lang="css" scoped>
</style>