import VueCookies from 'vue-cookies'
import Vue from 'vue'
import BootstrapVue from 'bootstrap-vue'
import 'vue-multiselect/dist/vue-multiselect.min.css'
import GetTextPlugin from 'vue-gettext'
// import translations from '@/assets/locale/translations.json'

import store from '@/store/index'
import App from './App'
import router from './router'

Vue.use(VueCookies)

Vue.config.productionTip = false

Vue.use(BootstrapVue)

Vue.use(GetTextPlugin, {
	availableLanguages: {
		ar: 'Arabic',
		en: 'English',
		es: 'Spanish',
		fr: 'French',
		ru: 'Russian',
		zh: 'Chinese'
	},
	defaultLanguage: 'en',
	languageVmMixin: {
		computed: {
			currentKebabCase() {
				return this.current.toLowerCase().replace('_', '-')
			}
		}
	},
	translations: { ar: {}, en: {}, es: {}, fr: {}, ru: {}, zh: {} },
	silent: false
})

new Vue({
	router,
	store,
	render: h => h(App)
}).$mount('#app')
