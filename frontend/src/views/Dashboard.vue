<template>
  <div class="animated fadeIn">
    <b-row>
      <b-col sm="6">
        <b-card v-if="basicDataReady">
          <div slot="header">
            <strong>Create new submission </strong>
          </div>

          <div>
            <b-input-group class="mb-2" prepend="Obligation">
              <multiselect trackBy="value" label="text" placeholder="" v-model="current.obligation" :options="obligations"></multiselect>
            </b-input-group>

            <b-input-group class="mb-2" prepend="Period">
               <multiselect trackBy="value" label="text" customTemplateText="<i class='fa fa-clock-o fa-lg'></i>" customTemplate="is_reporting_open" placeholder="" v-model="current.reporting_period" :options="periods">
               </multiselect>
            </b-input-group>

            <b-input-group class="mb-2" prepend="Party">
               <multiselect trackBy="value" label="text" placeholder="" v-model="current.party" :options="parties"></multiselect>
            </b-input-group>

            <b-btn v-if="basicDataReady" :disabled="!(current.obligation && current.reporting_period && current.party)" variant="primary" @click="addSubmission">Create submission</b-btn>
          </div>

        </b-card>
      </b-col>

        <b-col sm="6">
          <b-card v-if="dataReady">
            <div slot="header">
              <strong>Continue working on your submissions </strong>
            </div>
            <b-row class="open-submissions-list">
              <b-col class="mb-3" v-if="submission.current_state === 'data_entry'" :key="submission.url" v-for="submission in submissions">
                  <router-link
                        class="btn btn-light submission-continue"
                        :to="{ name: getFormName(submission.obligation), query: {submission: submission.url}} "
                      >
                  <div class="detail-header">
                         Submission details:
                  </div>
                  <div>
                   <i class="fa fa-calendar fa-lg"></i> {{getSubmissionInfo(submission).period()}}
                  </div>
                  <div>
                   <i class="fa fa-certificate fa-lg"></i> {{getSubmissionInfo(submission).obligation()}}
                  </div>
                  <div>
                    <i class="fa fa-globe fa-lg"></i> {{getSubmissionInfo(submission).party()}}
                  </div>
                  <div>
                    <i class="fa fa-archive fa-lg"></i> Version {{submission.version}}
                  </div>
                </router-link>
              </b-col>
            </b-row>
          </b-card>
        </b-col>
    </b-row>
    <b-row>
      <b-col sm="12">
          <b-card no-body v-if="dataReady">
            <template slot="header">
              <b-row>
              <b-col>Latest submissions</b-col>

              <b-col>
                  <b-form-group horizontal label="Per page" class="mb-0">
                    <b-form-select :options="table.pageOptions" v-model="table.perPage" />
                  </b-form-group>
              </b-col>
              <b-col style="text-align: right"><b-form-checkbox type="checkbox" v-model="table.filters.isCurrent">Show all versions</b-form-checkbox></b-col>
              </b-row>
            </template>
            <b-container fluid>
              <b-row class="mt-2">
                <b-col>
                    <b-input-group prepend="Search">
                      <b-form-input v-model="table.filters.search" placeholder="Type to Search" />
                      <b-input-group-append>
                        <b-btn variant="primary" :disabled="!table.filters.search" @click="table.filters.search = ''">Clear</b-btn>
                      </b-input-group-append>
                    </b-input-group>
                </b-col>
                <b-col>
                    <b-input-group prepend="Filter by party">
                      <b-form-select v-model="table.filters.party" :options="sortOptionsParties"></b-form-select>
                      <b-input-group-append>
                        <b-btn variant="primary" :disabled="!table.filters.party" @click="table.filters.party = ''">Clear</b-btn>
                      </b-input-group-append>
                    </b-input-group>
                </b-col>
              </b-row>
              <b-row class="mt-2 mb-2">
                <b-col>
                    <b-input-group prepend="Period from:">
                      <b-form-select v-model="table.filters.period_start" :options="sortOptionsPeriodFrom">
                      </b-form-select>
                      <b-input-group-append>
                        <b-btn variant="primary" :disabled="!table.filters.period_start" @click="table.filters.period_start = ''">Clear</b-btn>
                      </b-input-group-append>
                    </b-input-group>
                </b-col>
                <b-col>
                    <b-input-group prepend="Period to:">
                      <b-form-select v-model="table.filters.period_end" :options="sortOptionsPeriodTo">
                      </b-form-select>
                      <b-input-group-append>
                        <b-btn variant="primary" :disabled="!table.filters.period_end" @click="table.filters.period_end = ''">Clear</b-btn>
                      </b-input-group-append>
                    </b-input-group>
                </b-col>
                <b-col>
                    <b-input-group prepend="Filter by obligation">
                      <b-form-select v-model="table.filters.obligation" :options="sortOptionsObligation"></b-form-select>
                      <b-input-group-append>
                        <b-btn variant="primary" :disabled="!table.filters.obligation" @click="table.filters.obligation = ''">Clear</b-btn>
                      </b-input-group-append>
                    </b-input-group>
                </b-col>
              </b-row>
              <b-table show-empty
                       outlined
                       bordered
                       hover
                       head-variant="light"
                       stacked="md"
                       :items="tableItems"
                       :fields="table.fields"
                       :current-page="table.currentPage"
                       :per-page="table.perPage"
                       :sort-by.sync="table.sortBy"
                       :sort-desc.sync="table.sortDesc"
                       :sort-direction="table.sortDirection"
                       :filter="table.filters.search"
                       @filtered="onFiltered"
                       ref="table"
              >
                <template slot="actions" slot-scope="row">
                  <b-button-group>
                    <router-link
                        class="btn btn-outline-primary"
                        :to="{ name: getFormName(row.item.details.obligation), query: {submission: row.item.details.url}} "
                      >
                      <span v-if="row.item.details.data_changes_allowed">
                        Edit
                      </span>
                      <span v-else>
                        View
                      </span>
                    </router-link>

                    <b-btn
                        v-if="row.item.details.is_cloneable"
                        variant="outline-primary"
                        @click="clone(row.item.details.url)"
                      >
                      Clone
                    </b-btn>

                    <b-btn
                      variant="outline-primary"
                      v-for="transition in row.item.details.available_transitions"
                      :key="transition"
                      @click="$store.dispatch('doSubmissionTransition', {submission: row.item.details.url, transition: transition, source: 'dashboard'})"
                    >
                      {{labels[transition]}}
                    </b-btn>

                    <b-btn
                        variant="outline-danger"
                        @click="removeSubmission(row.item.details.url)"
                        v-if="row.item.details.data_changes_allowed"
                      >
                      Delete
                    </b-btn>
                  </b-button-group>
                  </template>
              </b-table>

              <b-row>
                <b-col md="6" class="my-1">
                  <b-pagination :total-rows="table.totalRows" :per-page="table.perPage" v-model="table.currentPage" class="my-0" />
                </b-col>
              </b-row>

            </b-container>
          </b-card>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import { cloneSubmission } from '@/api/api'
import errorHandling from '@/mixins/errorHandling'
import Multiselect from '@/mixins/modifiedMultiselect'
// import Multiselect from "vue-multiselect"
import { mapGetters } from 'vuex'
import labels from '@/assets/labels'

export default {
	name: 'Dashboard',
	data() {
		return {
			current: {
				obligation: null,
				reporting_period: null,
				party: null
			},
			labels: labels.general,
			table: {
				fields: [
					{
						key: 'obligation', label: 'Obligation', sortable: true, sortDirection: 'desc', class: 'text-center'
					},
					{
						key: 'reporting_period', label: 'Reporting period', sortable: true, class: 'text-center'
					},
					{
						key: 'reporting_party', label: 'Reporting party', sortable: true, sortDirection: 'desc', class: 'text-center'
					},
					{
						key: 'version', label: 'Version', sortable: true, sortDirection: 'desc', class: 'text-center'
					},
					{
						key: 'current_state', label: 'State', sortable: true, class: 'text-center'
					},
					{
						key: 'last_updated', label: 'Last modified', sortable: true, class: 'text-center'
					},
					{ key: 'actions', label: 'Actions', class: 'text-center' }
				],
				currentPage: 1,
				perPage: 10,
				totalRows: 5,
				pageOptions: [5, 25, 100],
				sortBy: null,
				sortDesc: false,
				sortDirection: 'asc',
				filters: {
					search: null,
					period_start: null,
					period_end: null,
					obligation: null,
					party: null,
					isCurrent: null
				},
				modalInfo: { title: '', content: '' }
			}

		}
	},

	created() {
		document.querySelector('body').classList.remove('aside-menu-lg-show')
		this.$store.dispatch('getDashboardParties')
		this.$store.dispatch('getDashboardPeriods')
		this.$store.dispatch('getDashboardObligations')
		this.$store.dispatch('getCurrentSubmissions')
	},

	components: {
		Multiselect
	},

	computed: {

		...mapGetters(['getSubmissionInfo']),

		tableItems() {
			const tableFields = []
			this.submissions.forEach((element) => {
				if (
					(this.table.filters.period_start ? this.getSubmissionInfo(element).period_start() >= this.table.filters.period_start : true)
          && (this.table.filters.period_end ? this.getSubmissionInfo(element).period_end() <= this.table.filters.period_end : true)
          && (this.table.filters.obligation ? this.getSubmissionInfo(element).obligation() === this.table.filters.obligation : true)
          && (this.table.filters.party ? this.getSubmissionInfo(element).party() === this.table.filters.party : true)
          && (this.table.filters.isCurrent ? true : (element.current_state === 'data_entry' ? true : !!(false || element.is_current)))
				) {
					tableFields.push({
						obligation: this.getSubmissionInfo(element).obligation(),
						reporting_period: this.getSubmissionInfo(element).period(),
						reporting_party: this.getSubmissionInfo(element).party(),
						current_state: element.current_state,
						version: element.version,
						last_updated: element.updated_at,
						details: element
					})
				}
			})
			this.table.totalRows = tableFields.length
			return tableFields
		},

		sortOptionsPeriodFrom() {
			return [...new Set(this.periods.map(f => f.start_date.split('-')[0]))]
		},

		sortOptionsPeriodTo() {
			return [...new Set(this.periods.map(f => f.end_date.split('-')[0]))]
		},

		sortOptionsObligation() {
			return [...new Set(this.submissions.map(f => this.getSubmissionInfo(f).obligation()))]
		},

		sortOptionsParties() {
			return [...new Set(this.submissions.map(f => this.getSubmissionInfo(f).party()))]
		},

		dataReady() {
			if (this.submissions
        && this.periods
        && this.obligations
        && this.parties
        && this.submissions.length) {
				return true
			}
			return false
		},

		periods() {
			return this.$store.state.dashboard.periods
		},
		parties() {
			return this.$store.state.dashboard.parties
		},
		obligations() {
			return this.$store.state.dashboard.obligations
		},
		submissions() {
			return this.$store.state.dashboard.submissions
		},

		basicDataReady() {
			if (this.periods
        && this.obligations
        && this.parties) {
				return true
			}
			return false
		}
	},

	methods: {
		addSubmission() {
			this.$store.dispatch('addSubmission', this.current).then(r => {
				const currentSubmission = this.submissions.find(sub => sub.id === r.id)
				this.$router.push({ name: this.getFormName(r.obligation), query: { submission: currentSubmission.url } })
			})
		},

		clone(url) {
			cloneSubmission(url).then(() => {
				this.$store.dispatch('getCurrentSubmissions')
				this.$store.dispatch('setAlert', { message: 'Submission cloned', variant: 'success' })
			}).catch(error => {
				this.$store.dispatch('setAlert', { message: errorHandling.handleError(error.response.data), variant: 'danger' })
				console.log(error)
			})
		},

		removeSubmission(url) {
			const r = confirm('Deleting the submission is ireversible. Are you sure ?')
			if (r === true) {
				this.$store.dispatch('removeSubmission', url)
			}
		},

		onFiltered(filteredItems) {
			// Trigger pagination to update the number of buttons/pages due to filtering
			this.table.totalRows = filteredItems.length
			this.table.currentPage = 1
		},

		getFormName(obligation) {
			return this.obligations.find(o => o.value === obligation).form_type
		}

	},

	watch: {
		'table.filters': {
			handler() {
				this.$refs.table.refresh()
			},
			deep: true
		}
	}
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter,
.fade-leave-to {
  opacity: 0;
}
.submission-continue span {
  margin-left: .5rem;
}

.submission-continue {
  border: 1px solid #eee;
  box-shadow: 1px 1px 3px #eee;
  text-align: left;
  display: block;
  padding: .5rem;
  margin: .5rem;
}

.submission-continue div:not(.detail-header) {
    background: white;
    color: #444;
    margin-left: -15px;
    margin-right: -15px;
    padding: .5rem 15px;
    border: 1px solid #eee;
}

.detail-header {
  margin-bottom: .5rem;
}
</style>
