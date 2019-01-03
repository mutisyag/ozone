<template>
  <div class="animated fadeIn">
    <b-row>
      <b-col v-if="basicDataReady && !currentUser.is_read_only" sm="4">
        <b-card>
          <div slot="header">
            <strong>Create submission</strong>
          </div>
					<small>Create a submission by specifying the obligation, the reporting period and the party name. All fields are mandatory.</small>
          <div class="create-submission mt-2">
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

            <b-btn v-if="basicDataReady" :disabled="!(current.obligation && current.reporting_period && current.party)" variant="primary" @click="addSubmission">Create</b-btn>
          </div>

        </b-card>
      </b-col>

        <b-col>
          <b-card v-if="basicDataReady">
            <div slot="header">
              <strong>My submissions </strong>
            </div>
						<table class="table table-hover classic-header">
							<thead>
								<tr>
									<th>Obligation</th>
									<th>Period</th>
									<th>Party</th>
									<th>Version</th>
									<th>Last modified</th>
									<th>Actions</th>
								</tr>
							</thead>
							<tbody>
								<tr :key="submission.url" v-for="submission in mySubmissions">
									<td>
                   {{getSubmissionInfo(submission).obligation()}}
									</td>
									<td>
										{{getSubmissionInfo(submission).period()}}
									</td>
									<td>
										{{getSubmissionInfo(submission).party()}}
									</td>
									<td>
                     {{submission.version}}
									</td>
									<td>
                     {{submission.updated_at}}
									</td>
									<td>
										<router-link :to="{ name: getFormName(submission.obligation), query: {submission: submission.url}}">
											Continue
										</router-link>
									</td>
								</tr>
							</tbody>
						</table>
          </b-card>
        </b-col>
    </b-row>
    <b-row>
      <b-col sm="12">
          <b-card no-body v-if="basicDataReady">
            <template slot="header">
              <b-row>
              <b-col><b>All submissions ({{table.totalRows}} records)</b></b-col>
              <b-col style="text-align: right"><b-form-checkbox type="checkbox" v-model="tableOptions.filters.showAllVersions">Show all versions</b-form-checkbox></b-col>
              </b-row>
            </template>
            <b-container fluid>
              <div class="mt-2 mb-2 dashboard-filters">
								<b-input-group prepend="Search">
									<b-form-input v-model="tableOptions.filters.search"/>
								</b-input-group>
								<b-input-group prepend="Obligation">
									<b-form-select v-model="tableOptions.filters.obligation" :options="sortOptionsObligation"></b-form-select>
								</b-input-group>
								<b-input-group prepend="Party">
									<b-form-select v-model="tableOptions.filters.party" :options="sortOptionsParties"></b-form-select>
								</b-input-group>
								<b-input-group style="width: 120px" prepend="From">
									<b-form-select v-model="tableOptions.filters.period_start" :options="sortOptionsPeriodFrom">
									</b-form-select>
								</b-input-group>
								<b-input-group style="width: 120px" prepend="To">
									<b-form-select v-model="tableOptions.filters.period_end" :options="sortOptionsPeriodTo">
									</b-form-select>
								</b-input-group>
								<b-btn @click="clearFilters">Clear</b-btn>
              </div>
              <b-table show-empty
                       outlined
                       bordered
                       hover
                       head-variant="light"
                       stacked="md"
                       :items="tableItems"
                       :fields="table.fields"
                       :per-page="tableOptions.perPage"
                       :sort-by.sync="tableOptions.sorting.sortBy"
                       :sort-desc.sync="tableOptions.sorting.sortDesc"
                       :sort-direction="tableOptions.sorting.sortDirection"
                       ref="table"
              >
                <template slot="actions" slot-scope="row">
                  <b-button-group>
                    <router-link
                        class="btn btn-outline-primary btn-sm"
                        :to="{ name: getFormName(row.item.details.obligation), query: {submission: row.item.details.url}} "
                      >
                      <span v-if="row.item.details.data_changes_allowed && !currentUser.is_read_only">
                        Edit
                      </span>
                      <span v-else>
                        View
                      </span>
                    </router-link>

                    <b-btn
                        variant="outline-primary"
                        @click="clone(row.item.details.url, row.item.details.obligation)"
												size="sm"
												:disabled="currentUser.is_read_only"
											>
                      Revise
                    </b-btn>

                    <b-btn
                      variant="outline-primary"
                      v-for="transition in row.item.details.available_transitions"
                      :key="transition"
											size="sm"
											:disabled="currentUser.is_read_only"
                      @click="$store.dispatch('doSubmissionTransition', {submission: row.item.details.url, transition: transition, source: 'dashboard'})"
                    >
                      {{labels[transition]}}
                    </b-btn>

                    <b-btn
                        variant="outline-danger"
                        @click="removeSubmission(row.item.details.url)"
                        v-if="row.item.details.data_changes_allowed"
												:disabled="currentUser.is_read_only"
												size="sm"
                      >
                      Delete
                    </b-btn>
                  </b-button-group>
                  </template>
              </b-table>

              <b-row>
                <b-col md="10" class="my-1">
                  <b-pagination :total-rows="tableOptions.totalRows" :per-page="tableOptions.perPage" v-model="tableOptions.currentPage" class="my-0" />
                </b-col>
								<b-col md="2">
                  <b-input-group horizontal prepend="Per page" class="mb-0">
                    <b-form-select :options="table.pageOptions" v-model="tableOptions.perPage" />
                  </b-input-group>
								</b-col>
              </b-row>

            </b-container>
          </b-card>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import { cloneSubmission } from '@/components/common/services/api'
import Multiselect from '@/components/common/ModifiedMultiselect'
import { mapGetters } from 'vuex'
import labels from '@/components/art7/dataDefinitions/labels'

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
						key: 'obligation', label: 'Obligation', sortable: true, sortDirection: 'desc'
					},
					{
						key: 'reporting_period', label: 'Period', sortable: true
					},
					{
						key: 'party', label: 'Party', sortable: true, sortDirection: 'desc'
					},
					{
						key: 'version', label: 'Version', sortable: true, sortDirection: 'desc'
					},
					{
						key: 'current_state', label: 'State', sortable: true
					},
					{
						key: 'updated_at', label: 'Last modified', sortable: true
					},
					{ key: 'actions', label: 'Actions' }
				],
				pageOptions: [10, 25, 100],
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
		this.$store.dispatch('getMyCurrentUser')
		this.$store.commit('updateBreadcrumbs', ['Dashboard'])
	},

	components: {
		Multiselect
	},

	computed: {

		...mapGetters(['getSubmissionInfo']),

		/* The problem

		Using item provider function as indicated in the documentation (https://bootstrap-vue.js.org/docs/components/table)
		for async pagination and filtering raises a few problems if the provider function or the function that fetches the data,
		also used in the provider function is called outside of the internal filter/pagination change watcher,
		like deleting an entry and trying to update the table after.

		Actually, the async call had some problems even if the calls where within the specified parameters, like perPage fiter.

		The solution

		1.Table items are provided to the table through a computed method that iterates through the list obtained via the async call.
		2.Filters/pagination are no longer specifically binded to the table. Instead, we use a watcher on tableOptions,
			doing a call for getting the filtered list of submissions every
		 	time a option changes in the tableOptions object, like pagination, filtering, perpage etc.
		3.Because the data is provided via computed, the table data also updates in the interface every time we get a new list of submissions,
			after doing actions like deleting, cloning or changing the state of a submission. */

		tableItems() {
			const tableFields = []
			if (this.submissions && this.submissions.length) {
				this.submissions.forEach((element) => {
					tableFields.push({
						obligation: this.getSubmissionInfo(element).obligation(),
						reporting_period: this.getSubmissionInfo(element).period(),
						party: this.getSubmissionInfo(element).party(),
						current_state: element.current_state,
						version: element.version,
						updated_at: element.updated_at,
						details: element
					})
				})
			}
			return tableFields
		},
		sortOptionsPeriodFrom() {
			return this.periods.map(f => {
				if (this.tableOptions.filters.period_end !== null
				&& f.start_date > this.tableOptions.filters.period_end) {
					return null
				}
				return {
					text: f.start_date.split('-')[0],
					value: f.start_date
				}
			}).filter(f => f !== null)
		},

		sortOptionsPeriodTo() {
			return this.periods.map(f => {
				if (this.tableOptions.filters.period_start !== null
				&& f.end_date < this.tableOptions.filters.period_start) {
					return null
				}
				return {
					text: f.start_date.split('-')[0],
					value: f.end_date
				}
			}).filter(f => f !== null)
		},

		sortOptionsObligation() {
			return this.obligations
		},

		sortOptionsParties() {
			return this.parties
		},

		dataReady() {
			if (this.submissions
        && this.periods
				&& this.currentUser
        && this.obligations
        && this.parties
        && this.submissions.length) {
				return true
			}
			return false
		},
		tableOptions() {
			return this.$store.state.dashboard.table
		},
		currentUser() {
			return this.$store.state.currentUser
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
		mySubmissions() {
			return this.$store.state.dashboard.mySubmissions
		},

		basicDataReady() {
			if (this.periods
        && this.obligations
				&& this.currentUser
        && this.parties) {
				return true
			}
			return false
		},
		tableOptionsExceptFilters() {
			const tableOptions = {
				sorting: this.$store.state.dashboard.table.sorting,
				currentPage: this.$store.state.dashboard.table.currentPage,
				perPage: this.$store.state.dashboard.table.perPage
			}
			return tableOptions
		}
	},

	methods: {
		addSubmission() {
			this.$store.dispatch('addSubmission', this.current).then(r => {
				const currentSubmission = this.submissions.find(sub => sub.id === r.id)
				this.$router.push({ name: this.getFormName(r.obligation), query: { submission: currentSubmission.url } })
			})
		},
		clearFilters() {
			Object.keys(this.tableOptions.filters).forEach(key => {
				this.tableOptions.filters[key] = null
			})
		},
		clone(url, obligation) {
			cloneSubmission(url).then((response) => {
				this.$router.push({ name: this.getFormName(obligation), query: { submission: response.data.url } })
				this.$store.dispatch('setAlert', {
					message: { __all__: ['Submission cloned'] },
					variant: 'success'
				})
			}).catch(error => {
				this.$store.dispatch('setAlert', {
					message: { ...error.response.data },
					variant: 'danger' })
				console.log(error)
			})
		},

		removeSubmission(url) {
			const r = confirm('Deleting the submission is ireversible. Are you sure ?')
			if (r === true) {
				this.$store.dispatch('removeSubmission', url)
			}
		},

		getFormName(obligation) {
			return this.obligations.find(o => o.value === obligation).form_type
		}

	},

	watch: {
		// TODO: the watchers trigger each other in the case when user is on page > 1 and selects a filter, causing 2 requests instead of 1
		'tableOptions.filters': {
			handler() {
				if (this.tableOptions.currentPage !== 1) {
					this.tableOptions.currentPage = 1
				}
				this.$store.dispatch('getCurrentSubmissions')
				this.$refs.table.refresh()
			},
			deep: true
		},
		tableOptionsExceptFilters: {
			handler() {
				this.$store.dispatch('getCurrentSubmissions')
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

.detail-header {
  margin-bottom: .5rem;
}
.dashboard-filters {
	display: flex;
}
.dashboard-filters > div {
	margin-right: 5px;
	min-width: 120px;
}
</style>
