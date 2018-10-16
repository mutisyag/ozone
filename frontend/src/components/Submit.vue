<template>
	  <b-btn @click="startSubmitting" variant="success">
        Submit
      </b-btn>
</template>

<script>

import {post} from '@/api/api'
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
        }
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
       post(this.submission[this.fields_to_save[field]], {}).then( (response) => {console.log(response) })
    },
  }
}
</script>

<style lang="css" scoped>
</style>