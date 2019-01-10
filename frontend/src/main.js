import VueCookies from 'vue-cookies'
import Vue from 'vue'
import BootstrapVue from 'bootstrap-vue'
import 'vue-multiselect/dist/vue-multiselect.min.css'
import GetTextPlugin from 'vue-gettext'
import translations from '@/assets/locale/translations.json'

import store from '@/store/index'
import App from './App'
import router from './router'

Vue.use(VueCookies)

Vue.config.productionTip = false

Vue.use(BootstrapVue)

Vue.use(GetTextPlugin, {
	availableLanguages: {
		en_GB: 'British English',
		en_US: 'American English',
		es_US: 'Español',
		fr_FR: 'Français',
		it_IT: 'Italiano'
	},
	defaultLanguage: 'en_US',
	languageVmMixin: {
		computed: {
			currentKebabCase() {
				return this.current.toLowerCase().replace('_', '-')
			}
		}
	},
	translations,
	silent: false
})

new Vue({
	router,
	store,
	render: h => h(App)
}).$mount('#app')
