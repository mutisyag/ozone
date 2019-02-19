import GetTextPlugin from 'vue-gettext'
import moment from 'moment'
import {
	fetchFromPublicDirectory
} from './api'

const getLanguageUrl = (languageKey) => `/translations/${languageKey}.json`

const defaultLanguage = 'en'
const translations = { ar: {}, en: {}, es: {}, fr: {}, ru: {}, zh: {} }

const initLanguages = (Vue) => {
	Vue.use(GetTextPlugin, {
		availableLanguages: {
			ar: 'العربية',
			zh: '中文',
			en: 'English',
			fr: 'Français',
			ru: 'Русский',
			es: 'Español'
		},
		defaultLanguage,
		languageVmMixin: {
			computed: {
				currentKebabCase() {
					return this.current.toLowerCase().replace('_', '-')
				}
			}
		},
		translations,
		silent: true
	})
}

const setLanguage = async (languageKey, vm) => {
	if (!translations[languageKey] || !Object.keys(translations[languageKey]).length) {
		const languageResponse = await fetchFromPublicDirectory(getLanguageUrl(languageKey))
		translations[languageKey] = languageResponse.data[languageKey]
	}
	vm.$language.current = languageKey
}

const dateFormat = (value, language, formatString) => {
	moment().locale(language)
	return moment(value).format(formatString || 'LL')
}

const dateFormatToYYYYMMDD = (value, language) => dateFormat(value, language, 'YYYY-MM-DD')

export {
	initLanguages,
	setLanguage,
	dateFormat,
	dateFormatToYYYYMMDD
}
