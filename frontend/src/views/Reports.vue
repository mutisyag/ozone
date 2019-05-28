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
              @click="generateReport"
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
    this.reports = [{ value: null, text: 'none' }]
  },
  components: {
    Multiselect
  },
  methods: {
    generateReport() {
    }
  }
}
</script>
