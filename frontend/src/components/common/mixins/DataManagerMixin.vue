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
      prefilled: false,
      preventMessage: this.$gettext('Do you really want to leave this page? You have unsaved changes!')
    }
  },

  async beforeRouteLeave(to, from, next) {
    if (this.alertUnsavedData()) {
      const answer = await this.$store.dispatch('openConfirmModal', { title: 'Please confirm', description: 'Do you really want to leave this page? You have unsaved changes!', $gettext: this.$gettext })
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
    this.$store.commit('resetStuff')
    this.$store.commit('resetDashboardFilters')
    this.doInitialStuff()
  },

  computed: {
    initialDataReady() {
      if (!this.form) {
        return false
      }
      for (const propertyPath of this.form.formDetails.dataNeeded) {
        const propValue = getPropertyValue(this.$store.state, propertyPath)
        if (propertyPath === 'submissionDefaultValues.submission_format') {
          // eslint-disable-next-line no-continue
          continue
        }
        if (!propValue) return false
      }

      const { dataNeeded } = this.form.formDetails
      Object.values(this.form.tabs).forEach(tab => {
        if (isObject(tab.form_fields)) {
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
            if (formField.selectedPropertyPath) {
              for (const propertyPath of dataNeeded) {
                if (formField.selectedPropertyPath === propertyPath) {
                  const propValue = getPropertyValue(this.$store.state, propertyPath)
                  if (formField.selected !== propValue) {
                    formField.selected = propValue
                  }
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
    doInitialStuff() {
      if (!this.submission) {
        this.$router.push({ name: 'Dashboard' })
      } else {
        window.addEventListener('beforeunload', this.alertUnsavedData)
        this.$store.dispatch('getInitialData', {
          $gettext: this.$gettext,
          submission: this.submission,
          formName: this.currentFormName,
          additionalAction: null
        }).then(() => {
          this.prePrefill()
          this.prefillComments()
        })
      }
    },
    alertUnsavedData(e) {
      const tabsWithData = []
      Object.values(this.form.tabs).forEach((tab) => {
        [false, 'edited'].includes(tab.status) && tabsWithData.push(tab.title)
      })
      if (tabsWithData.length && e) {
        // Cancel the event as stated by the standard.
        e.preventDefault()
        // Chrome requires returnValue to be set.
        e.returnValue = this.preventMessage
        return this.preventMessage
      } if (tabsWithData.length) {
        return tabsWithData.length
      }
      return null
    },

    prePrefill() {
      const { form } = this.$store.state
      const prefill_data = this.$store.state.current_submission
      Object.keys(form.tabs).forEach((tab) => {
        if (form.tabs[tab].endpoint_url && Object.keys(this.$store.state.current_submission).includes(form.tabs[tab].endpoint_url)) {
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

    prefillComments() {
      fetch(this.$store.state.current_submission.submission_remarks).then(response => {
        this.$store.dispatch('prefillComments', response.data)
      }).catch(error => {
        console.log(error)
      })
    },

    prefill(tabName, data) {
      let ordering_id = 0
      if (Array.isArray(this.form.tabs[tabName].form_fields)) {
        ordering_id = Math.max(...data.map(row => row.ordering_id))
        const sortedData = tabName === 'has_emissions' ? data.sort((a, b) => a.ordering_id - b.ordering_id) : data
        sortedData.forEach(item => {
          if (item.substance || item.blend) {
            this.$store.dispatch('createSubstance', {
              $gettext: this.$gettext,
              substanceList: item.substance ? [item.substance] : null,
              currentSectionName: tabName,
              groupName: null,
              country: null,
              blendList: item.blend ? [item.blend] : null,
              prefillData: item
            })
          } else {
            this.$store.dispatch('createRow', {
              $gettext: this.$gettext,
              currentSectionName: tabName,
              prefillData: item
            })
          }
        })
        if (tabName === 'has_emissions') {
          this.$store.commit('setTabOrderingId', { tabName, ordering_id })
        }
      }
      if (isObject(this.form.tabs[tabName].form_fields)) {
        const [prefillData] = data
        this.$store.commit('prefillTab', { tabName, data: prefillData })
      }
      this.$store.commit('setTabStatus', { tab: tabName, value: true })
    }

  },
  watch: {
    '$language.current': {
      handler() {
        this.$store.commit('setForm', { formName: this.currentFormName, $gettext: this.$gettext })
      }
    }
  }
}
</script>
