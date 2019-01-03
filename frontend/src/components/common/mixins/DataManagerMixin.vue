<script>
import {
	fetch
} from '@/components/common/services/api.js'
import {
	isObject,
	getPropertyValue
} from '@/components/common/services/utilsService'

export default {
	name: 'DataManager',

	data() {
		return {
			currentFormName: this.$route.name,
			submission: this.$route.query.submission,
			prefilled: false
		}
	},

	beforeRouteLeave(to, from, next) {
		if (process.env.NODE_ENV !== 'development') {
			if (this.alertUnsavedData()) {
				const answer = window.confirm('Do you really want to leave? you have unsaved changes!')
				if (answer) {
					next()
				} else {
					next(false)
				}
			} else {
				next()
			}
		} else {
			next()
		}
	},

	created() {
		if (!this.submission) {
			this.$router.push({ name: 'Dashboard' })
		} else {
			if (process.env.NODE_ENV !== 'development') {
				window.addEventListener('beforeunload', this.alertUnsavedData)
			}
			this.$store.dispatch('getInitialData', { submission: this.submission, formName: this.currentFormName }).then(() => {
				this.prePrefill()
			})
		}
	},

	computed: {
		initialDataReady() {
			if (!this.form) {
				return false
			}
			for (const propertyPath of this.form.formDetails.dataNeeded) {
				const propValue = getPropertyValue(this.$store.state, propertyPath)
				if (!propValue) return false
			}

			const { dataNeeded } = this.form.formDetails

			Object.values(this.form.tabs).forEach(tab => {
				if (isObject(tab.form_fields)) {
					console.log(tab.form_fields)
					for (const formFieldPropName in tab.form_fields) {
						const formField = tab.form_fields[formFieldPropName]
						if (formField.optionsStatePropertyPath) {
							for (const propertyPath of dataNeeded) {
								if (formField.optionsStatePropertyPath === propertyPath) {
									const propValue = getPropertyValue(this.$store.state, propertyPath)
									formField.options = propValue
									break
								}
							}
						}
					}
				}
			})

			return this.prefilled
		},

		form() {
			return this.$store.state.form
		}

	},

	methods: {

		alertUnsavedData(e) {
			const tabsWithData = []
			Object.values(this.form.tabs).forEach((tab) => {
				[false, 'edited'].includes(tab.status) && tabsWithData.push(tab.title)
			})

			if (tabsWithData.length && e) {
				// Cancel the event as stated by the standard.
				e.preventDefault()
				// Chrome requires returnValue to be set.
				e.returnValue = ''
			} else if (tabsWithData.length) {
				return tabsWithData.length
			}
			return null
		},

		prePrefill() {
			const { form } = this.$store.state
			const prefill_data = this.$store.state.current_submission
			Object.keys(form.tabs).forEach((tab) => {
				if (form.tabs[tab].endpoint_url) {
					fetch(prefill_data[form.tabs[tab].endpoint_url]).then(response => {
						if (response.data.length) {
							this.$store.commit('setTabStatus', { tab, value: 'saving' })
							this.prefill(form.tabs[tab].name, response.data)
						} else {
							console.log('updatingnewtab', tab)
							this.$store.commit('updateNewTabs', tab)
						}
					}).catch(error => {
						console.log(error)
					})
				}
			})
			this.prefilled = true
		},
		prefill(tabName, data) {
			let ordering_id = 0
			if (Array.isArray(this.form.tabs[tabName].form_fields)) {
				ordering_id = Math.max(...data.map(row => row.ordering_id))
				const sortedData = data.sort((a, b) => a.ordering_id - b.ordering_id)
				sortedData.forEach(item => {
					if (item.substance || item.blend) {
						this.$store.dispatch('createSubstance', {
							substanceList: item.substance ? [item.substance] : null,
							currentSectionName: tabName,
							groupName: null,
							country: null,
							blendList: item.blend ? [item.blend] : null,
							prefillData: item
						})
					} else {
						this.$store.dispatch('createRow', {
							currentSectionName: tabName,
							prefillData: item
						})
					}
				})
				this.$store.commit('setTabOrderingId', { tabName, ordering_id })
			}
			if (isObject(this.form.tabs[tabName].form_fields)) {
				const [prefillData] = data
				this.$store.commit('prefillTab', { tabName, data: prefillData })
			}
			this.$store.commit('setTabStatus', { tab: tabName, value: true })
		}

	}
}
</script>
