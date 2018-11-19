import Vue from 'vue'
import Vuex from 'vuex'
import form from '@/assets/form.js'
import tableRowConstructor from '@/mixins/tableRowConstructor'

Vue.use(Vuex)


const store = new Vuex.Store({
  state: {
  	permissions: {
  		dashboard: null,
  		form: null,
  		actions: null,
  	},
    newTabs: [],
    form: form,
  },


  actions: {
     prefillQuestionaire(context,data){
      Object.keys(data).forEach( (element, index) => {
        context.commit('updateQuestionaireField', {value: data[element], field: element})
      });
    },

    createSubstance(context,data){
    let iterator = data.substanceList
    let substancesHere = (data.substanceList && data.substanceList.length) ? data.substanceList.some( (el) => {return el !== null}) : false
    let blendsHere = (data.blendList && data.blendList.length) ? data.blendList.some( (el) => {return el !== null}) : false

      if(substancesHere) {
       for(let substance of data.substanceList) {
            let inner_fields = tableRowConstructor.getInnerFields(data.currentSectionName, substance, data.groupName, data.country, null, data.prefillData)
            context.commit('addSubstance', {sectionName: data.currentSectionName, row: inner_fields})
          }
      } else if(blendsHere) {
         for(let blend of data.blendList) {
          console.log(blend)
            let inner_fields = tableRowConstructor.getInnerFields(data.currentSectionName, null, data.groupName, data.country, blend, data.prefillData)
            context.commit('addSubstance', {sectionName: data.currentSectionName, row: inner_fields})
          }
      }
    },

    prefillEmissionRow(context, data){
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
              if(data){
                Object.keys(data).forEach( (element, index) => {
                  row[element].selected = data[element] 
                });
              }
            context.commit('addEmissionsRow', row)
    }
  },

  mutations: {
    
    // questionaire
    updateQuestionaireField(state, data){
       store.state.form.tabs.questionaire_questions.form_fields[data.field] = data.value
    },

    // addsubstance
    addSubstance(state, data) {
       store.state.form.tabs[data.sectionName].form_fields.push(data.row)
    },

    addEmissionsRow(state, data) {
       store.state.form.tabs.tab_7.form_fields.push(data)
    },


    setTabStatus(state, data) {
      store.state.form.tabs[data.tab].status = data.value
    },

    // permissions
  	updateDashboardPermissions(state, permission) {
  		state.permissions.dashboard = permission
  	},
  	updateFormPermissions(state, permission) {
  		state.permissions.form = permission
  	},
  	updateActionsPermissions(state, permission) {
  		state.permissions.actions = permission
  	},

    // form state
    updateNewTabs(state, tab) {
      state.newTabs.push(tab)
    },

    tabHasBeenSaved(state,tab){
      state.newTabs.splice(state.newTabs.indexOf(field),1)
    }
  }
})


export default store