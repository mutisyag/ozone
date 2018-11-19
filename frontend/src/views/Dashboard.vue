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



            <b-btn v-if="basicDataReady" variant="primary" @click="addSubmission">Create submission</b-btn>
          </div>

        </b-card>
      </b-col>

      <b-col sm="12">
          <b-card no-body v-if="dataReady">
            <template slot="header">
              <b-row>
              <b-col>Latest submissions</b-col>
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
                  <b-form-group horizontal label="Per page" class="mb-0">
                    <b-form-select :options="table.pageOptions" v-model="table.perPage" />
                  </b-form-group>
                </b-col>
              </b-row>
              <b-row>
                <b-col md="6" class="my-1">
                  <b-form-group horizontal label="Filter by period" class="mb-0">
                    <b-input-group>
                      <b-form-select v-model="table.filters.period" :options="sortOptionsPeriod">
                      </b-form-select>
                      <b-input-group-append>
                        <b-btn :disabled="!table.filters.period" @click="table.filters.period = ''">Clear</b-btn>
                      </b-input-group-append>
                    </b-input-group>
                  </b-form-group>
                </b-col>
                <b-col md="6" class="my-1">
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
                        class="nav-link btn btn-primary btn-sm"
                        :to="{ name: 'Form', query: {submission: row.item.details.url}} "
                      >
                      form
                    </router-link>
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

import {getSubmissions, getSubmissionsVersions, getPeriods, getObligations, createSubmission, getParties} from '@/api/api';

export default {
  name: 'Dashboard',
  data () {
    return {
    	submissions: null,
      submissionsVersions: null,
      periods: null,
      obligations: null,
      parties: null,
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
            { key: 'actions', label: 'Actions', 'class': 'text-center' },
          ],
          currentPage: 1,
          perPage: 10,
          totalRows: 5,
          pageOptions: [ 5, 10, 15, 20, 25, 50 ],
          sortBy: null,
          sortDesc: false,
          sortDirection: 'asc',
          filters: {
            search: null,
            period: null,
            obligation: null,
            isCurrent: null,
          },
          modalInfo: { title: '', content: '' }
        }
      
    }
  },

  beforeCreate(){
   document.querySelector('body').classList.remove('aside-menu-lg-show')

    getSubmissions().then( response => {
        this.submissions = response.data
    })

    getSubmissionsVersions().then( response => {
        this.submissionsVersions = response.data
    })

   getParties().then( response => {
    let parties_temp = [];
      for (let country of response.data) {
        parties_temp.push({ value: country.id, text: country.name})
      }
      this.parties = JSON.parse(JSON.stringify(parties_temp))
    })

    getPeriods().then( response => {
      let periods_temp = [];
      for(let period of response.data) {
        periods_temp.push({value: period.id, text:period.name})
      }
      this.periods = JSON.parse(JSON.stringify(periods_temp)) 
    })

    getObligations().then( response => {
      let obligations_temp = [];
      for(let obligation of response.data) {
        obligations_temp.push({value: obligation.id, text: obligation.name})
      }
      this.obligations = JSON.parse(JSON.stringify(obligations_temp)) 
    })

  },


  computed: {
    tableItems(){
      let tableFields = []
      this.submissionsVersions.forEach( (element, index) => {
        if(
          (this.table.filters.period ? this.getSumissionInfo(element).period() === this.table.filters.period : true)
          &&
          (this.table.filters.obligation ? this.getSumissionInfo(element).obligation() === this.table.filters.obligation : true)
          && 
          (this.table.filters.isCurrent ? true : (element.current_state === 'data_entry' ? true : false || element.is_current ? true : false) )
         ) {
          tableFields.push({obligation: this.getSumissionInfo(element).obligation(),
           reporting_period: this.getSumissionInfo(element).period(),
           reporting_party: this.getSumissionInfo(element).party(),
           current_state: element.current_state,
           version: element.version,
           details: element})
        }
      
      });
      this.table.totalRows = tableFields.length
      return tableFields
    },

    sortOptionsPeriod () {
      let options =  this.tableItems.map(f => { return { text: f.reporting_period, value: f.reporting_period } })
      options.unshift({text: '', value: null})
      return options
    },

    sortOptionsObligation () {
      let options =  this.tableItems.map(f => { return { text: f.obligation, value: f.obligation } })
      options.unshift({text: '', value: null})
      return options
    },


    dataReady(){ 
      if(this.submissionsVersions 
        && this.submissions 
        && this.periods 
        && this.obligations 
        && this.parties 
        && this.submissions.length) {
        return true
      }
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
      createSubmission(this.current).then( (response) => { console.log(response);this.getSubmissions()} )
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
        }
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