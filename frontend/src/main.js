import 'core-js/es6'
import VueCookies from 'vue-cookies'
import Vue from 'vue'
import BootstrapVue from 'bootstrap-vue'
import 'vue-multiselect/dist/vue-multiselect.min.css'

import store from '@/store/index'
import App from './App'
import router from './router'
import { initLanguages } from '@/components/common/services/languageService'

Vue.use(VueCookies)

Vue.config.productionTip = false

Vue.use(BootstrapVue)

initLanguages(Vue)

new Vue({
	router,
	store,
	render: h => h(App)
}).$mount('#app')
