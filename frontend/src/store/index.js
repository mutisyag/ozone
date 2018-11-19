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
      for(let questionaire_question in data) {
       let current_field = store.state.form.tabs.tab_1.form_fields.find( field =>  field.name === questionaire_question )
       if(current_field){
        context.commit('updateQuestionaireField', {value: data[questionaire_question], field: current_field.name})
       }
      }
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
    }
  },

  mutations: {
    
    // questionaire
    updateQuestionaireField(state, value){
       let current_field = store.state.form.tabs.tab_1.form_fields.find( field =>  field.name === value.field )
       current_field.selected = value.value
    },

    // addsubstance
    addSubstance(state, data) {
       let current_tab = Object.keys(store.state.form.tabs).find((tab) => {if(store.state.form.tabs[tab].name === data.sectionName) return tab})
       store.state.form.tabs[current_tab].form_fields.push(data.row)
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