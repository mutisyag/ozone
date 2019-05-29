<template>
  <div v-if="parties && periods && reports">
    <b-row>
      <b-col sm="7">
        <b-card>
          <div slot="header">
            <strong>
              <span v-translate>Generate report</span>
            </strong>
          </div>
          <small>
            <span
              v-translate
            >Generate report by selecting the report type and filtering by party and period. Only one filter can have multiple values.</span>
          </small>
          <div class="create-submission mt-2">
            <b-input-group id="reports_selector" class="mb-2" :prepend="$gettext('Reports')">
              <multiselect
                :placeholder="$gettext('Select option')"
                trackBy="value"
                label="text"
                v-model="selected.reports"
                :options="reports"
              />
            </b-input-group>

            <b-input-group id="period_selector" class="mb-2" :prepend="$gettext('Period')">
              <multiselect
                :placeholder="$gettext('Select option')"
                trackBy="value"
                :multiple="selected.parties.length > 1 ? false : true"
                label="text"
                v-model="selected.periods"
                :options="periods"
              />
            </b-input-group>

            <b-input-group id="party_selector" class="mb-2" :prepend="$gettext('Party')">
              <multiselect
                :placeholder="$gettext('Select option')"
                trackBy="value"
                label="text"
                :multiple="selected.periods.length > 1 ? false : true"
                v-model="selected.parties"
                :options="parties"
              />
            </b-input-group>

            <b-btn
              variant="primary"
              @click="createUrlAndParams"
            >
              <span v-translate>Generate report</span>
            </b-btn>
          </div>
          </b-card>
        </b-col>
      </b-row>
  </div>
</template>
<script>
// import Multiselect from '@/components/common/ModifiedMultiselect'
import Multiselect from 'vue-multiselect'
import { fetch } from '@/components/common/services/api'

export default {
  data() {
    return {
      reports: null,
      parties: null,
      periods: null,
      selected: {
        parties: [],
        periods: [],
        reports: null
      }
    }
  },
  async created() {
    this.parties = await this.$store.dispatch('getDashboardParties')
    this.periods = await this.$store.dispatch('getDashboardPeriods')
    this.reports = await this.$store.dispatch('getReportsList')
  },
  components: {
    Multiselect
  },
  methods: {
    parseParams(params) {
      const keys = Object.keys(params)
      let options = ''

      keys.forEach((key) => {
        const isParamTypeObject = typeof params[key] === 'object'
        const isParamTypeArray = isParamTypeObject && (params[key].length >= 0)

        if (!isParamTypeObject) {
          options += `${key}=${params[key]}&`
        }

        if (isParamTypeObject && isParamTypeArray) {
          params[key].forEach((element) => {
            options += `${key}=${element}&`
          })
        }
      })

      return options ? options.slice(0, -1) : options
    },
    createUrlAndParams() {
      const params = {
        period: Array.isArray(this.selected.periods) ? this.selected.periods.map(p => p.value) : this.selected.periods.value,
        party: Array.isArray(this.selected.parties) ? this.selected.parties.map(p => p.value) : this.selected.parties.value
      }
      const url = `reports/${this.selected.reports.value}/`
      this.generateReport(url, `${this.selected.reports.value}.pdf`, params)
    },
    async generateReport(url, fileName, params) {
      console.log(params)
      try {
        const downloaded = await fetch(url, { params, 'paramsSerializer': p => this.parseParams(p) }, { responseType: 'arraybuffer' })
        const blob = new Blob([downloaded.data])
        if (navigator.msSaveBlob) {
          return navigator.msSaveBlob(blob, fileName)
        }
        const download_url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = download_url
        link.setAttribute('download', fileName)
        document.body.appendChild(link)
        link.click()
        link.parentNode.removeChild(link)
      } catch (e) {
        console.log('download error', e)
      }
    }
  }
}
</script>
