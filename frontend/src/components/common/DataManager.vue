<template>
  <div>
    <tabsmanager
    v-if="initialDataReady"
    :submission="submission"
    >
    </tabsmanager>
  </div>
</template>

<script>
import tabsManager from '@/components/art7/TabsManager'
import {
	fetch
} from '@/components/common/services/api.js'

export default {
	name: 'DataManager',
	components: {
		tabsmanager: tabsManager
	},

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
			for (const path of this.form.formDetails.dataNeeded) {
				const propNames = path.split('.')
				const propValue = propNames.reduce((prop, propName) => prop[propName], this.$store.state)
				if (!propValue) return false
			}
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
				if (form.tabs[tab].endpoint_url && tab !== 'questionaire_questions') {
					fetch(prefill_data[form.tabs[tab].endpoint_url]).then(response => {
						if (response.data.length) {
							this.$store.commit('setTabStatus', { tab, value: 'saving' })
							this.prefill(form.tabs[tab].name, response.data)
						} else {
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
			const ordering_id = Math.max(...data.map(row => row.ordering_id))
			const sortedData = data.sort((a, b) => a.ordering_id - b.ordering_id)

			sortedData.forEach(item => {
				// substanceList, currentSectionName, groupName, currentSection, country, blend, prefillData
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

			this.$store.commit('setTabStatus', { tab: tabName, value: true })
			this.$store.commit('setTabOrderingId', { tabName, ordering_id })
		}

	}
}
</script>
