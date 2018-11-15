import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)


const store = new Vuex.Store({
  state: {
  	permissions: {
  		dashboard: null,
  		form: null,
  		actions: null,
  	},
  },


  mutations: {
  	updateDashboardPermissions(state, permission) {
  		state.permissions.dashboard = permission
  	},
  	updateFormPermissions(state, permission) {
  		state.permissions.form = permission
  	},
  	updateActionsPermissions(state, permission) {
  		state.permissions.actions = permission
  	}
  }
})


export default store