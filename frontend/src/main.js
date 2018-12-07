import VueCookies from 'vue-cookies'
import Vue from 'vue'
import store from '@/store/index'
import BootstrapVue from 'bootstrap-vue'
import App from './App'
import router from './router'
import 'vue-multiselect/dist/vue-multiselect.min.css'

Vue.use(VueCookies)

Vue.config.productionTip = false

Vue.use(BootstrapVue)

new Vue({
	router,
	store,
	render: h => h(App)
}).$mount('#app')
