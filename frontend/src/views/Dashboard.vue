<template>
  <div class="animated fadeIn">
    <b-row>
      <b-col v-if="basicDataReady && !currentUser.is_read_only" sm="4">
        <b-card>
			<div slot="header">
				<strong><span v-translate>Create submission</span></strong>
			</div>
			<small><span v-translate>Create a submission by specifying the obligation, the reporting period and the party name. All fields are mandatory.</span></small>
			<div class="create-submission mt-2">
				<b-input-group id="obligation_selector" class="mb-2" :prepend="$gettext('Obligation')">
					<multiselect trackBy="value" label="text" v-model="current.obligation" :options="obligations"></multiselect>
				</b-input-group>

				<b-input-group id="period_selector"  class="mb-2" :prepend="$gettext('Period')">
					<multiselect trackBy="value" label="text" customTemplateText="<i class='fa fa-clock-o fa-lg'></i>" customTemplate="is_reporting_open" v-model="current.reporting_period" :options="periods">
				</multiselect>
				</b-input-group>

				<b-input-group id="party_selector" class="mb-2" :prepend="$gettext('Party')">
					<multiselect trackBy="value" label="text" :disabled="Boolean(currentUser.party)" v-model="current.party" :options="parties"></multiselect>
				</b-input-group>

				<b-btn v-if="basicDataReady" :disabled="!(current.obligation && current.reporting_period && current.party)" variant="primary" @click="addSubmission"><span v-translate>Create</span></b-btn>
			</div>
        </b-card>
      </b-col>

        <b-col>
          <b-card v-if="basicDataReady">
				<div slot="header">
					<strong><span v-translate='{totalRows: dataEntryTable.totalRows}'>Data entry submissions (%{totalRows} records)</span></strong>
				</div>
				<div v-if="currentUser.is_secretariat" class="mt-2 mb-2">
					<div class="filter-group mb-2">
						<b-input-group :prepend="$gettext('Search')">
							<b-form-input v-model="dataEntryTable.search"/>
						</b-input-group>
						<b-input-group :prepend="$gettext('Obligation')">
							<b-form-select v-model="dataEntryTable.filters.obligation" :options="sortOptionsObligation"></b-form-select>
						</b-input-group>
					</div>
					<div class="filter-group">
						<b-input-group :prepend="$gettext('Party')">
							<b-form-select :disabled="Boolean(currentUser.party)" v-model="dataEntryTable.filters.party" :options="sortOptionsParties"></b-form-select>
						</b-input-group>
						<b-input-group style="width: 120px" :prepend="$gettext('From')">
							<b-form-select v-model="dataEntryTable.filters.period_start" :options="sortOptionsPeriodFrom">
							</b-form-select>
						</b-input-group>
						<b-input-group style="width: 120px" :prepend="$gettext('To')">
							<b-form-select v-model="dataEntryTable.filters.period_end" :options="sortOptionsPeriodTo">
							</b-form-select>
						</b-input-group>
						<b-btn @click="Object.keys(dataEntryTable.filters).forEach(key => dataEntryTable.filters[key] = null)"><span v-translate>Clear</span></b-btn>
					</div>
				</div>
				<b-table show-empty
									outlined
									bordered
									hover
									head-variant="light"
									stacked="md"
									:filter="dataEntryTable.search"
									:items="dataEntryTableItems"
									:fields="dataEntryTableFields"
									:per-page="dataEntryTable.perPage"
									:current-page="dataEntryTable.currentPage"
									ref="dataEntryTable"
									@filtered="onFiltered">
						<template slot="actions" slot-scope="row">
							<router-link
									class="btn btn-outline-primary btn-sm"
									:to="{ name: getFormName(row.item.details.obligation), query: {submission: row.item.details.url}}">
								<span v-if="row.item.details.can_edit_data" v-translate>Continue</span>
								<span v-else v-translate>View</span>
							</router-link>
						</template>
			</b-table>
			<b-row v-if="currentUser.is_secretariat">
				<b-col md="9" class="my-1">
				<b-pagination :total-rows="dataEntryTable.totalRows" :per-page="dataEntryTable.perPage" v-model="dataEntryTable.currentPage" class="my-0" />
				</b-col>
				<b-col md="3">
					<b-input-group horizontal :prepend="$gettext('Per page')" class="mb-0">
						<b-form-select :options="dataEntryTable.pageOptions" v-model="dataEntryTable.perPage" />
					</b-input-group>
				</b-col>
			</b-row>
          </b-card>
        </b-col>
    </b-row>
    <b-row>
      <b-col sm="12">
          <b-card no-body v-if="basicDataReady">
            <template slot="header">
              <b-row>
				<b-col><b><span v-translate='{totalRows: tableOptions.totalRows}'>All submissions (%{totalRows} records)</span></b></b-col>
				<b-col style="text-align: right"><b-form-checkbox type="checkbox" v-model="tableOptions.filters.showAllVersions"><span v-translate>Show all versions</span></b-form-checkbox></b-col>
              </b-row>
            </template>
            <b-container fluid>
              <div  class="mt-2 mb-2 dashboard-filters">
					<b-input-group :prepend="$gettext('Search')">
						<b-form-input v-model="tableOptions.filters.search"/>
					</b-input-group>
					<b-input-group :prepend="$gettext('Obligation')">
						<b-form-select v-model="tableOptions.filters.obligation" :options="sortOptionsObligation"></b-form-select>
					</b-input-group>
					<b-input-group :prepend="$gettext('Party')">
						<b-form-select :disabled="Boolean(currentUser.party)" v-model="tableOptions.filters.party" :options="sortOptionsParties"></b-form-select>
					</b-input-group>
					<b-input-group style="width: 120px" :prepend="$gettext('From')">
						<b-form-select v-model="tableOptions.filters.period_start" :options="sortOptionsPeriodFrom">
						</b-form-select>
					</b-input-group>
					<b-input-group style="width: 120px" :prepend="$gettext('To')">
						<b-form-select v-model="tableOptions.filters.period_end" :options="sortOptionsPeriodTo">
						</b-form-select>
					</b-input-group>
					<b-btn @click="clearFilters"><span v-translate>Clear</span></b-btn>
              </div>
              <b-table show-empty
                       outlined
                       bordered
                       hover
                       head-variant="light"
                       stacked="md"
                       :items="tableItems"
                       :fields="tableFields"
                       :per-page="tableOptions.perPage"
                       :sort-by.sync="tableOptions.sorting.sortBy"
                       :sort-desc.sync="tableOptions.sorting.sortDesc"
                       :sort-direction="tableOptions.sorting.sortDirection"
                       ref="table">
                <template slot="actions" slot-scope="row">
                  <b-button-group>
                    <router-link
                        class="btn btn-outline-primary btn-sm"
                        :to="{ name: getFormName(row.item.details.obligation), query: {submission: row.item.details.url}}">
                      <span v-translate v-if="row.item.details.can_edit_data && !currentUser.is_read_only">
                        Edit
                      </span>
                      <span v-translate v-else>
                        View
                      </span>
                    </router-link>

                    <b-btn
                        variant="outline-primary"
                        @click="clone(row.item.details.url, row.item.details.obligation)"
												size="sm"
												v-if="row.item.details.is_cloneable"
												:disabled="currentUser.is_read_only">
                      <span v-translate>Revise</span>
                    </b-btn>

                    <b-btn
						variant="outline-primary"
						v-for="transition in row.item.details.available_transitions"
						:key="transition"
						size="sm"
						:disabled="currentUser.is_read_only"
						@click="$store.dispatch('doSubmissionTransition', {$gettext, transition, submission: row.item.details.url, source: 'dashboard'})">
							<span>{{labels[transition]}}</span>
                    </b-btn>

                    <b-btn
                        variant="outline-danger"
                        @click="removeSubmission(row.item.details.url)"
                        v-if="row.item.details.can_edit_data"
						:disabled="currentUser.is_read_only"
						size="sm">
                      <span v-translate>Delete</span>
                    </b-btn>
                  </b-button-group>
                  </template>
              </b-table>

              <b-row>
                <b-col md="10" class="my-1">
                  <b-pagination :total-rows="tableOptions.totalRows" :per-page="tableOptions.perPage" v-model="tableOptions.currentPage" class="my-0" />
                </b-col>
				<b-col md="2">
                  <b-input-group horizontal :prepend="$gettext('Per page')" class="mb-0">
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
import { getCommonLabels } from '@/components/common/dataDefinitions/labels'

export default {
	name: 'Dashboard',
	data() {
		return {
			current: {
				obligation: null,
				reporting_period: null,
				party: null
			},
			labels: getCommonLabels(this.$gettext),
			table: {
				pageOptions: [10, 25, 100]
			},
			tableOptionsCurrentPageWasSetFromWatcher: false,
			dataEntryTable: {
				currentPage: 1,
				perPage: 10,
				totalRows: 0,
				sorting: {
					sortBy: 'updated_at',
					sortDesc: true,
					sortDirection: 'asc'
				},
				search: null,
				filters: {
					period_start: null,
					period_end: null,
					obligation: null,
					party: null
				},
				pageOptions: [10, 25, 100]
			}
		}
	},

	created() {
		document.querySelector('body').classList.remove('aside-menu-lg-show')
		this.$store.dispatch('getDashboardParties')
		this.$store.dispatch('getDashboardPeriods')
		this.$store.dispatch('getDashboardObligations')
		this.$store.dispatch('getMyCurrentUser')
		this.updateBreadcrumbs()
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
		tableFields() {
			return [
				{
					key: 'obligation', label: this.$gettext('Obligation'), sortable: true, sortDirection: 'desc'
				},
				{
					key: 'reporting_period', label: this.$gettext('Period'), sortable: true
				},
				{
					key: 'party', label: this.$gettext('Party'), sortable: true, sortDirection: 'desc'
				},
				{
					key: 'version', label: this.$gettext('Version'), sortable: true, sortDirection: 'desc'
				},
				{
					key: 'current_state', label: this.$gettext('State'), sortable: true
				},
				{
					key: 'updated_at', label: this.$gettext('Last modified'), sortable: true
				},
				{ key: 'actions', label: this.$gettext('Actions') }
			]
		},
		dataEntryTableItems() {
			const tableFields = []
			const { filters } = this.dataEntryTable
			const filtersExist = Object.keys(filters).some(f => filters[f])
			if (this.mySubmissions && this.mySubmissions.length) {
				this.mySubmissions.forEach((element) => {
					if (filtersExist && this.checkFilters(filters, element)) {
						return
					}
					const row = {
						obligation: this.getSubmissionInfo(element).obligation(),
						reporting_period: this.getSubmissionInfo(element).period(),
						party: this.getSubmissionInfo(element).party(),
						version: element.version,
						updated_at: element.updated_at,
						details: element
					}
					tableFields.push(row)
				})
			}
			return tableFields
		},
		dataEntryTableFields() {
			return [
				{
					key: 'obligation', label: this.$gettext('Obligation'), sortable: true, sortDirection: 'desc'
				},
				{
					key: 'reporting_period', label: this.$gettext('Period'), sortable: true
				},
				{
					key: 'party', label: this.$gettext('Party'), sortable: true, sortDirection: 'desc'
				},
				{
					key: 'version', label: this.$gettext('Version'), sortable: true, sortDirection: 'desc'
				},
				{
					key: 'updated_at', label: this.$gettext('Last modified'), sortable: true
				},
				{
					key: 'actions', label: this.$gettext('Actions')
				}
			]
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
			const current = this.$store.state.currentUser
			if (current) this.current.party = current.party
			return current
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
			const { sorting, currentPage, perPage } = this.$store.state.dashboard.table
			const tableOptions = {
				sorting,
				currentPage,
				perPage
			}
			return tableOptions
		}
	},

	methods: {
		updateBreadcrumbs() {
			this.$store.commit('updateBreadcrumbs', [this.$gettext('Dashboard')])
		},
		addSubmission() {
			this.$store.dispatch('addSubmission', {
				$gettext: this.$gettext,
				submission: this.current
			}).then(r => {
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
					$gettext: this.$gettext,
					message: { __all__: [this.$gettext('New version created')] },
					variant: 'success'
				})
			}).catch(error => {
				this.$store.dispatch('setAlert', {
					$gettext: this.$gettext,
					message: { ...error.response.data },
					variant: 'danger' })
				console.log(error)
			})
		},

		checkFilters(filters, element) {
			if (filters.obligation && element.obligation !== filters.obligation) {
				return true
			}
			if (filters.party && element.party !== filters.party) {
				return true
			}
			if (filters.period_start && parseInt(this.getSubmissionInfo(element).period()) < parseInt(filters.period_start.split('-')[0])) {
				return true
			}
			if (filters.period_end && parseInt(this.getSubmissionInfo(element).period()) > parseInt(filters.period_end.split('-')[0])) {
				return true
			}
			return false
		},

		removeSubmission(url) {
			const r = confirm(this.$gettext('Deleting the submission is ireversible. Are you sure ?'))
			if (r === true) {
				this.$store.dispatch('removeSubmission', {
					$gettext: this.$gettext,
					submissionUrl: url
				})
			}
		},

		getFormName(obligation) {
			return this.obligations.find(o => o.value === obligation).form_type
		},
		onFiltered(filteredItems) {
			this.dataEntryTable.totalRows = filteredItems.length
			this.dataEntryTable.currentPage = 1
		}
	},

	watch: {
		'$language.current': {
			handler() {
				this.updateBreadcrumbs()
			}
		},
		'tableOptions.filters': {
			handler() {
				if (this.tableOptions.currentPage !== 1) {
					this.tableOptions.currentPage = 1
					this.tableOptionsCurrentPageWasSetFromWatcher = true
				}
				this.$store.dispatch('getCurrentSubmissions')
				if (!this.$refs.table) return
				this.$refs.table.refresh()
			},
			deep: true
		},
		tableOptionsExceptFilters: {
			handler() {
				if (this.tableOptionsCurrentPageWasSetFromWatcher) {
					this.tableOptionsCurrentPageWasSetFromWatcher = false
					return
				}
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
.dashboard-filters > div,
.filter-group > div {
	margin-right: 5px;
	min-width: 130px;
}

.filter-group {
	display: flex;
}
</style>
