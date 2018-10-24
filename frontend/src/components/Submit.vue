<template>
  <span>
    
    <b-btn @click="validateDuplicates" style="border-top-left-radius: 0;border-bottom-left-radius:0" variant="success">
        Submit
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

      <b-alert variant="success"
             dismissible
             style="
                  position: fixed;
                  top: 7rem;
                  left: 50%;
                  transform: translateX(-50%);
                  padding: 3rem;
                  z-index: 1;
                  font-weight: bold;"
             :show="showDismissibleAlertSave"
             @dismissed="showDismissibleAlertSave=false"
             >
             Form saved
      </b-alert>
  </span>

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
        findDuplicates: {},
        showDismissibleAlert: false,
        showDismissibleAlertSave: false,
        current_duplicates: '',
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
              "source_party": 1,
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


    validateDuplicates(){
      this.errorMessage = null
      this.duplicatesFound = []
      this.findDuplicates = {}
      for(let tab in this.data.tabs) {
        if(['has_imports', 'has_exports', 'has_nonparty'].includes(this.data.tabs[tab].name) && this.data.tabs[tab].form_fields.length){ 
            this.data.tabs[tab].form_fields.forEach( form_field => {
              let substance = form_field.substance
              
              substance.type != 'blend' ? 
                !this.findDuplicates[substance.selected.text] && (this.findDuplicates[substance.selected.text] = []) 
              : 
                !this.findDuplicates[substance.selected.name] && (this.findDuplicates[substance.selected.name] = [])
              
              substance.inner_fields.forEach( inner_field => {
                 if(['destination_party', 'source_party', 'trade_party'].includes(inner_field.name) && inner_field.selected) {
                    substance.type != 'blend' ? this.findDuplicates[substance.selected.text].push(inner_field.selected.text + ' - in ' +  `"${this.data.tabs[tab].title}"`) : this.findDuplicates[substance.selected.name].push(inner_field.selected.text + ' - in ' + `"${this.data.tabs[tab].title}"`)
                 } 
              })

          });
        }
      }

      for(let entry in this.findDuplicates) {
        // let found = this.findDuplicates[entry].find((element, index) => (this.findDuplicates[entry].indexOf(element) != index));
        let arrayDuplicates = (a) => {let d=[]; a.sort((a,b) => a-b).reduce((a,b)=>{a==b&&!d.includes(a)&&d.push(a); return b}); return d};
        // console.log('findduplicates', this.findDuplicates[entry])
        let duplicates = []
        if(this.findDuplicates[entry].length){
          duplicates = arrayDuplicates(this.findDuplicates[entry])
        }
        if(duplicates.length) {
          this.duplicatesFound.push(entry + ' : ' + duplicates)
        }
      }
      this.current_duplicates = 'Found duplicates: <br>'
      
      console.log('duplicatesfound', this.duplicatesFound, this.findDuplicates)

      if(this.duplicatesFound.length) {
        this.duplicatesFound.forEach(duplicate => this.current_duplicates += `<b>  (${duplicate})  </b>  `)
        this.current_duplicates += '<br> Please correct the errors before submiting the form again<br>'
        this.showDismissibleAlert = true
        this.duplicatesFound = []
        this.findDuplicates = {}
      } else {
        this.showDismissibleAlert = false
        this.startSubmitting()
      }

    },

  	startSubmitting(){
      this.errorMessage = null
      this.current_duplicates = null
      this.submitQuestionaireData('questionaire_questions')
      for(let questionnaire_field of this.data.tabs.tab_1.form_fields) {
        if(questionnaire_field.selected) {
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
       // for some reason calling [0,1].forEach() in a certain iteration causes erros. Probably babel stuff
       let small_iterator = [0,1]
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
          let substance = form_field.substance
          let save_obj = JSON.parse(JSON.stringify(this.form_fields[field]))
            
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
       }
        
        this.$validator._base.validateAll().then((result) => {
          if (result) {
            post(this.submission[this.fields_to_save[field]], current_tab_data).then( (response) => {
              this.showDismissibleAlertSave = true
              }).catch((error) => {
              console.log(this.$validator)
              
              console.log('here error',error)
            })
          } else {

            this.errorMessage = "Please correct the errors before saving the form again"
            this.showDismissibleAlert = true
            
            console.log('errors', result)
          }
        });





    },
  }
}
</script>

<style lang="css" scoped>

.alert b {
  margin-right: 1rem;
}

</style>