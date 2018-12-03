<template>
  <div>
    <tabsmanager
    v-if="initialDataReady"
    :submission="submission"
    >
    </tabsmanager>
    <div v-else class="spinner">
      <div class="loader"></div>
    </div>
  </div>
</template>

<script>
import tabsManager from './TabsManager'
import {
	fetch
} from '@/api/api.js'

export default {
	name: 'DataManager',
	components: {
		tabsmanager: tabsManager
	},

	data() {
		return {
			form: this.$store.state.form,
			current_submission: null,
			prefilled: false,
			submission: this.$route.query.submission,
			fields_to_prefill: {
				questionaire_questions: 'article7questionnaire',
				has_imports: 'article7imports',
				has_exports: 'article7exports',
				has_produced: 'article7productions',
				has_destroyed: 'article7destructions',
				has_nonparty: 'article7nonpartytrades',
				has_emissions: 'article7emissions'
			},
			fields_to_get: {
				// 'questionaire_questions' : 'article7questionnaire_url',
				has_imports: 'article7imports_url',
				has_exports: 'article7exports_url',
				has_produced: 'article7productions_url',
				has_destroyed: 'article7destructions_url',
				has_nonparty: 'article7nonpartytrades_url',
				has_emissions: 'article7emissions_url'
			}
		}
	},

	beforeRouteLeave(to, from, next) {
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
	},

	created() {
		if (!this.submission) {
			this.$router.push({ name: 'Dashboard' })
		} else {
			window.addEventListener('beforeunload', this.alertUnsavedData)
			this.$store.dispatch('getInitialData', this.submission).then(() => {
				this.prePrefill()
			})
		}
	},

	computed: {
		initialDataReady() {
			return this.$store.state.initialData.countryOptions
              && this.$store.state.initialData.substances
              && this.$store.state.initialData.blends
              && this.$store.state.current_submission
              && this.$store.state.initialData.display.substances
              && this.$store.state.initialData.display.blends
              && this.$store.state.initialData.display.countries
              && this.prefilled
    }
  },

  methods: {

    alertUnsavedData(e) {
      const tabsWithData = []
      Object.values(this.$store.state.form.tabs).forEach((tab) => {
        [false, 'edited'].includes(tab.status) && tabsWithData.push(tab.title)
      })

      if (tabsWithData.length && e) {
        // Cancel the event as stated by the standard.
        e.preventDefault()
        // Chrome requires returnValue to be set.
        e.returnValue = ''
        console.log(tabsWithData)
      } else if (tabsWithData.length) {
        return tabsWithData.length
      }
      return null
    },

    prePrefill() {
      const form = this.$store.state.form

      const prefill_data = this.$store.state.current_submission
      Object.keys(form.tabs).forEach((tab) => {
        if (this.fields_to_get[tab]) {
          fetch(prefill_data[this.fields_to_get[tab]]).then(response => {
            if (response.data.length) {
              this.$store.commit('setTabStatus', { tab: tab, value: 'saving' })
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

      if (tabName !== 'has_emissions') {
        sortedData.forEach(item => {
          // substanceList, currentSectionName, groupName, currentSection, country, blend, prefillData
          this.$store.dispatch('createSubstance', {
            substanceList: item.substance ? [item.substance] : null,
            currentSectionName: tabName,
            groupName: null,
            country: null,
            blendList: item.blend ? [item.blend] : null,
            prefillData: item
          })
        })
      } else {
        sortedData.forEach(el => this.$store.dispatch('prefillEmissionsRow', el))
      }
      this.$store.commit('setTabStatus', { tab: tabName, value: true })
      this.$store.commit('setTabOrderingId', { tabName, ordering_id })
    }

  }
}
</script>

<style lang="css" scoped>

.spinner {
    z-index: 1;
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(0,0,0,0.2);
    display: flex;
    justify-content: center;
    align-items: center;
}

.loader {
  border: 16px solid #f3f3f3;
  border-radius: 50%;
   border-top: 16px solid blue;
   border-right: 16px solid green;
   border-bottom: 16px solid red;
   border-left: 16px solid pink;
  width: 120px;
  height: 120px;
  -webkit-animation: spin 2s linear infinite; /* Safari */
  animation: spin 2s linear infinite;
}

/* Safari */
@-webkit-keyframes spin {
  0% { -webkit-transform: rotate(0deg); }
  100% { -webkit-transform: rotate(360deg); }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
