<template>
  <div class="animated fadeIn">
    <b-row>
      <b-col sm="5">
        <b-card v-if="basicDataReady">
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

        <b-col sm="7">
          <b-card v-if="dataReady">
            <div slot="header">
              <strong>My submissions </strong>
            </div>
						<table class="table table-striped table-hover classic-header">
							<thead>
								<tr>
									<th>Obligation</th>
									<th>Reporting period</th>
									<th>Version</th>
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
                     {{submission.version}}
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
          <b-card no-body v-if="dataReady">
            <template slot="header">
              <b-row>
              <b-col>All submissions</b-col>
              <b-col style="text-align: right"><b-form-checkbox type="checkbox" v-model="tableOptions.filters.isCurrent">Show all versions</b-form-checkbox></b-col>
              </b-row>
            </template>
            <b-container fluid>
              <b-row class="mt-2 mb-2">
                <b-col>
                    <b-input-group prepend="Search">
                      <b-form-input v-model="tableOptions.filters.search"/>
                    </b-input-group>
                </b-col>
                <b-col>
                    <b-input-group prepend="By party">
                      <b-form-select v-model="tableOptions.filters.party" :options="sortOptionsParties"></b-form-select>
                    </b-input-group>
                </b-col>
								<b-col cols="2">
                    <b-input-group prepend="From">
                      <b-form-select v-model="tableOptions.filters.period_start" :options="sortOptionsPeriodFrom">
                      </b-form-select>
                    </b-input-group>
                </b-col>
                <b-col cols="2">
                    <b-input-group prepend="To">
                      <b-form-select v-model="tableOptions.filters.period_end" :options="sortOptionsPeriodTo">
                      </b-form-select>
                    </b-input-group>
                </b-col>
                <b-col cols="3">
                    <b-input-group prepend="By obligation">
                      <b-form-select v-model="tableOptions.filters.obligation" :options="sortOptionsObligation"></b-form-select>
                    </b-input-group>
                </b-col>
								<b-col cols="1">
									<b-btn @click="clearFilters">Clear</b-btn>
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
                       :current-page="tableOptions.currentPage"
                       :per-page="tableOptions.perPage"
                       :sort-by.sync="tableOptions.sorting.sortBy"
                       :sort-desc.sync="tableOptions.sorting.sortDesc"
                       :sort-direction="tableOptions.sorting.sortDirection"
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
                        variant="outline-primary"
                        @click="clone(row.item.details.url)"                      >
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
                <b-col md="9" class="my-1">
                  <b-pagination :total-rows="tableOptions.totalRows" :per-page="tableOptions.perPage" v-model="tableOptions.currentPage" class="my-0" />
                </b-col>
								<b-col md="3">
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
import Multiselect from '@/components/common/modifiedMultiselect'
// import Multiselect from "vue-multiselect"
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
						key: 'reporting_period', label: 'Reporting period', sortable: true
					},
					{
						key: 'party', label: 'Reporting party', sortable: true, sortDirection: 'desc'
					},
					{
						key: 'version', label: 'Version', sortable: true, sortDirection: 'desc'
					},
					{
						key: 'current_state', label: 'State', sortable: true
					},
					{
						key: 'last_updated', label: 'Last modified', sortable: true
					},
					{ key: 'actions', label: 'Actions' }
				],
                pageOptions: [5, 25, 100],
				modalInfo: { title: '', content: '' }
			}

		}
	},

	created() {
		document.querySelector('body').classList.remove('aside-menu-lg-show')
		this.$store.dispatch('getDashboardParties')
		this.$store.dispatch('getDashboardPeriods')
		this.$store.dispatch('getDashboardObligations')
		this.$store.dispatch('getMyCurrentSubmissions')
		this.$store.dispatch('getCurrentSubmissions')
		this.$store.commit('updateBreadcrumbs', ['Dashboard'])
	},

	components: {
		Multiselect
	},

	computed: {

		...mapGetters(['getSubmissionInfo']),

		sortOptionsPeriodFrom() {
			return this.periods.map(f => {
			    return {
					text: f.start_date.split('-')[0],
					value: f.start_date
			    }
            })
		},

		sortOptionsPeriodTo() {
			return this.periods.map(f => {
			    return {
					text: f.start_date.split('-')[0],
					value: f.end_date
			    }
            })
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
        && this.parties) {
				return true
			}
			return false
		}
	},

	methods: {
	    tableItems(ctxt) {
	        return this.$store.dispatch('getCurrentSubmissions').then((data) => {
                const tableFields = []
                this.submissions.forEach((element) => {
                    tableFields.push({
                        obligation: this.getSubmissionInfo(element).obligation(),
                        reporting_period: this.getSubmissionInfo(element).period(),
                        party: this.getSubmissionInfo(element).party(),
                        current_state: element.current_state,
                        version: element.version,
                        last_updated: element.updated_at,
                        details: element
                    })
                })
                return tableFields
            })
        },

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
		clone(url) {
			cloneSubmission(url).then(() => {
				this.$store.dispatch('getCurrentSubmissions')
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
		'tableOptions.filters': {
			handler() {
				this.tableOptions.currentPage = 1
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

.detail-header {
  margin-bottom: .5rem;
}
</style>
