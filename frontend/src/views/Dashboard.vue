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
              <b-form-select placeholder="Select obligation" v-model="current.obligation" :options="obligations"></b-form-select>
            </b-input-group>
            
            <b-input-group class="mb-2" prepend="Period">
              <b-form-select placeholder="Select period" v-model="current.reporting_period" :options="periods"></b-form-select>
            </b-input-group>

            <b-input-group class="mb-2" prepend="Party">
              <b-form-select placeholder="Select period" v-model="current.party" :options="parties"></b-form-select>
            </b-input-group>



            <b-btn v-if="basicDataReady" :disabled="!(current.obligation && current.reporting_period && current.party)" variant="primary" @click="addSubmission">Create submission</b-btn>
          </div>

        </b-card>
      </b-col>

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
              <b-row>
                <b-col md="6" class="my-1">
                  <b-form-group horizontal label="Search" class="mb-0">
                    <b-input-group>
                      <b-form-input v-model="table.filters.search" placeholder="Type to Search" />
                      <b-input-group-append>
                        <b-btn :disabled="!table.filters.search" @click="table.filters.search = ''">Clear</b-btn>
                      </b-input-group-append>
                    </b-input-group>
                  </b-form-group>
                </b-col>
                <b-col md="6" class="my-1">
                  <b-form-group horizontal label="Filter by party" class="mb-0">
                    <b-input-group>
                      <b-form-select v-model="table.filters.party" :options="sortOptionsParties"></b-form-select>
                      <b-input-group-append>
                        <b-btn :disabled="!table.filters.party" @click="table.filters.party = ''">Clear</b-btn>
                      </b-input-group-append>
                    </b-input-group>
                  </b-form-group>
                </b-col>
              </b-row>
              <b-row>
                <b-col md="4" class="my-1">
                  <b-form-group horizontal label="Period from:" class="mb-0">
                    <b-input-group>
                      <b-form-select v-model="table.filters.period_start" :options="sortOptionsPeriodFrom">
                      </b-form-select>
                      <b-input-group-append>
                        <b-btn :disabled="!table.filters.period_start" @click="table.filters.period_start = ''">Clear</b-btn>
                      </b-input-group-append>
                    </b-input-group>
                  </b-form-group>
                </b-col>
                <b-col md="4" class="my-1">
                  <b-form-group horizontal label="Period to:" class="mb-0">
                    <b-input-group>
                      <b-form-select v-model="table.filters.period_end" :options="sortOptionsPeriodTo">
                      </b-form-select>
                      <b-input-group-append>
                        <b-btn :disabled="!table.filters.period_end" @click="table.filters.period_end = ''">Clear</b-btn>
                      </b-input-group-append>
                    </b-input-group>
                  </b-form-group>
                </b-col>
                <b-col md="4" class="my-1">
                  <b-form-group horizontal label="Filter by obligation" class="mb-0">
                    <b-input-group>
                      <b-form-select v-model="table.filters.obligation" :options="sortOptionsObligation"></b-form-select>
                      <b-input-group-append>
                        <b-btn :disabled="!table.filters.obligation" @click="table.filters.obligation = ''">Clear</b-btn>
                      </b-input-group-append>
                    </b-input-group>
                  </b-form-group>
                </b-col>
              </b-row>
              <b-table show-empty
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
                    <router-link
                        class="btn btn-primary"
                        :to="{ name: 'Form', query: {submission: row.item.details.url}} "
                      >
                      <span v-if="row.item.details.data_changes_allowed">
                        Edit
                      </span>
                      <span v-else>
                        View
                      </span>
                    </router-link>

                    <b-btn
                        variant="danger"
                        @click="removeSubmission(row.item.details.url)"
                      >
                      Delete
                    </b-btn>

                    <b-btn
                        variant="primary"
                        @click="clone(row.item.details.url)"
                      >
                      Clone
                    </b-btn>
                  </template>
              </b-table>

              <b-row>
                <b-col md="6" class="my-1">
                  <b-pagination :total-rows="table.totalRows" :per-page="table.perPage" v-model="table.currentPage" class="my-0" />
                </b-col>
              </b-row>

            </b-container fluid>
          </b-card>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import {cloneSubmission} from '@/api/api'

export default {
  name: 'Dashboard',
  data () {
    return {

      current: {
        obligation: null,
        reporting_period: null,
        party: null,
      },

      table: {
          fields: [
            { key: 'obligation', label: 'Obligation', sortable: true, sortDirection: 'desc', 'class': 'text-center' },
            { key: 'reporting_period', label: 'Reporting period', sortable: true, 'class': 'text-center' },
            { key: 'reporting_party', label: 'Reporting party', sortable: true, sortDirection: 'desc', 'class': 'text-center'},
            { key: 'version', label: 'Version', sortable: true, sortDirection: 'desc' , 'class': 'text-center'},
            { key: 'current_state', label: 'State', sortable: true, 'class': 'text-center'},
            { key: 'last_updated', label: 'Last modified', sortable: true, 'class': 'text-center'},
            { key: 'actions', label: 'Actions', 'class': 'text-center' },
          ],
          currentPage: 1,
          perPage: 10,
          totalRows: 5,
          pageOptions: [ 5, 25, 100 ],
          sortBy: null,
          sortDesc: false,
          sortDirection: 'asc',
          filters: {
            search: null,
            period_start: null,
            period_end: null,
            obligation: null,
            party: null,
            isCurrent: null,
          },
          modalInfo: { title: '', content: '' }
        }
      
    }
  },

  created(){
   document.querySelector('body').classList.remove('aside-menu-lg-show')
   this.$store.dispatch('getDashboardParties')
   this.$store.dispatch('getDashboardPeriods')
   this.$store.dispatch('getDashboardObligations')
   this.$store.dispatch('getCurrentSubmissions')
  },


  computed: {
    tableItems(){
      let tableFields = []
      console.log(this.submissions)
      this.submissions.forEach( (element, index) => {
        if(
          (this.table.filters.period_start ? this.getSumissionInfo(element).period_start() >= this.table.filters.period_start : true)
          &&
          (this.table.filters.period_end ? this.getSumissionInfo(element).period_end() <= this.table.filters.period_end : true)
          &&
          (this.table.filters.obligation ? this.getSumissionInfo(element).obligation() === this.table.filters.obligation : true)
          && 
          (this.table.filters.party ? this.getSumissionInfo(element).party() === this.table.filters.party : true)
          &&
          (this.table.filters.isCurrent ? true : (element.current_state === 'data_entry' ? true : false || element.is_current ? true : false) )
         ) {
          tableFields.push({obligation: this.getSumissionInfo(element).obligation(),
           reporting_period: this.getSumissionInfo(element).period(),
           reporting_party: this.getSumissionInfo(element).party(),
           current_state: element.current_state,
           version: element.version,
           last_updated: element.updated_at,
           details: element,
         })
        }
      
      });
      this.table.totalRows = tableFields.length
      return tableFields
    },

    sortOptionsPeriodFrom () {
      return [...new Set(this.periods.map(f => f.start_date.split('-')[0] ))]
    },


    sortOptionsPeriodTo () {
      return [...new Set(this.periods.map(f => f.end_date.split('-')[0] ))]
    },


    sortOptionsObligation () {
      return [...new Set(this.submissions.map(f => this.getSumissionInfo(f).obligation() ))]
    },
    
    sortOptionsParties () {
      return [...new Set(this.submissions.map(f => this.getSumissionInfo(f).party() ))]
    },

    dataReady(){ 
      if(this.submissions 
        && this.periods 
        && this.obligations 
        && this.parties 
        && this.submissions.length) {
        return true
      }
    },

    periods(){
      return this.$store.state.dashboard.periods
    },
    parties(){
      return this.$store.state.dashboard.parties
    },
    obligations(){
      return this.$store.state.dashboard.obligations
    },
    submissions(){
      return this.$store.state.dashboard.submissions
    },

    basicDataReady(){
      if(this.periods 
        && this.obligations 
        && this.parties){
          return true
      }
    }
  },

  methods: {
    addSubmission() {
      this.$store.dispatch('addSubmission', this.current)
    },


    clone(url){
      cloneSubmission(url).then(response => {
        console.log(resposne.data)
        this.$store.dispatch('setAlert', { message: 'Submission cloned', variant: 'success' })
      }).catch(error => {
        this.$store.dispatch('setAlert', { message: 'Unable to clone submission', variant: 'danger' })
        console.log(error)
      })
    },

    removeSubmission(url) {
      const r = confirm("Deleting the submission is ireversible. Are you sure ?");
      if (r == true) {
        this.$store.dispatch('removeSubmission', url)
      }
    },

    onFiltered (filteredItems) {
      // Trigger pagination to update the number of buttons/pages due to filtering
      this.table.totalRows = filteredItems.length
      this.table.currentPage = 1
    },


    getSumissionInfo(submission){
      let submissionInfo = {
        obligation: () => {
          return this.obligations.find( a => { return a.value === submission.obligation }).text
        },
        period: () => {
          return this.periods.find(a => {return a.value === submission.reporting_period}).text
        },
        party: () => {
          return this.parties.find(a => { return a.value === submission.party}).text
        },
        period_start: () => {
          return this.periods.find(a => {return a.value === submission.reporting_period}).start_date.split('-')[0]
        },
        period_end: () => {
          return this.periods.find(a => {return a.value === submission.reporting_period}).end_date.split('-')[0]
        },
      }
      return submissionInfo
    },

  },



watch: {
    'table.filters': {
        handler: function () {
              this.$refs.table.refresh()
        },
        deep: true
    }
},
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
</style>