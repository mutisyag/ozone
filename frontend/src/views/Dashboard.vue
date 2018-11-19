<template>
  <div class="animated fadeIn">
    <b-row>
      <b-col sm="6">
        <b-card v-if="periods && obligations && parties">
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

            <b-input-group v-if="parties" class="mb-2" prepend="Party">
              <b-form-select placeholder="Select period" v-model="current.party" :options="parties"></b-form-select>
            </b-input-group>



            <b-btn v-if="periods && obligations && parties" variant="primary" @click="addSubmission">Create submission</b-btn>
          </div>

        </b-card>
      </b-col>

      <b-col sm="12">
          <b-card no-body header="Latest submissions" v-if="submissions && periods && obligations && parties && submissions.length">
            <b-container fluid>
              <b-row>
                <b-col md="6" class="my-1">
                  <b-form-group horizontal label="Filter" class="mb-0">
                    <b-input-group>
                      <b-form-input v-model="table.filter" placeholder="Type to Search" />
                      <b-input-group-append>
                        <b-btn :disabled="!table.filter" @click="table.filter = ''">Clear</b-btn>
                      </b-input-group-append>
                    </b-input-group>
                  </b-form-group>
                </b-col>
                <b-col md="6" class="my-1">
                  <b-form-group horizontal label="Sort" class="mb-0">
                    <b-input-group>
                      <b-form-select v-model="table.sortBy" :options="table.sortOptions">
                        <option slot="first" :value="null">-- none --</option>
                      </b-form-select>
                      <b-form-select :disabled="!table.sortBy" v-model="table.sortDesc" slot="append">
                        <option :value="false">Asc</option>
                        <option :value="true">Desc</option>
                      </b-form-select>
                    </b-input-group>
                  </b-form-group>
                </b-col>
                <b-col md="6" class="my-1">
                  <b-form-group horizontal label="Sort direction" class="mb-0">
                    <b-input-group>
                      <b-form-select v-model="table.sortDirection" slot="append">
                        <option value="asc">Asc</option>
                        <option value="desc">Desc</option>
                        <option value="last">Last</option>
                      </b-form-select>
                    </b-input-group>
                  </b-form-group>
                </b-col>
                <b-col md="6" class="my-1">
                  <b-form-group horizontal label="Per page" class="mb-0">
                    <b-form-select :options="table.pageOptions" v-model="table.perPage" />
                  </b-form-group>
                </b-col>
              </b-row>
              <b-table show-empty
                       stacked="md"
                       :items="tableItems"
                       :fields="table.fields"
                       :current-page="table.currentPage"
                       :per-page="table.perPage"
                       :filter="table.filter"
                       :sort-by.sync="table.sortBy"
                       :sort-desc.sync="table.sortDesc"
                       :sort-direction="table.sortDirection"
                       @filtered="onFiltered"
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

import {getSubmissions, getPeriods, getObligations, createSubmission, getParties} from '@/api/api';

export default {
  name: 'Dashboard',
  data () {
    return {
    	submissions: null,
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
            { key: 'actions', label: 'Actions', 'class': 'text-center' },
          ],
          currentPage: 1,
          perPage: 10,
          totalRows: 5,
          pageOptions: [ 5, 10, 15 ],
          sortBy: null,
          sortDesc: false,
          sortDirection: 'asc',
          filter: null,
          modalInfo: { title: '', content: '' }
        }
      
    }
  },

  created(){
   document.querySelector('body').classList.remove('aside-menu-lg-show')

    getSubmissions().then( response => {
        this.submissions = response.data
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
        periods_temp.push({value: period.id, text: `${period.name} (${period.start_date} - ${period.end_date})`})
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
      this.submissions.forEach( (element, index) => {
        tableFields.push({obligation: this.getSumissionInfo(element).obligation(),
         reporting_period: this.getSumissionInfo(element).period(),
         reporting_party: this.getSumissionInfo(element).party(),
         version: element.version,
         details: element})
      });
      this.table.totalRows = tableFields.length
      return tableFields
    },
  },

  methods: {
    addSubmission() {
      createSubmission(this.current).then( (response) => { console.log(response);this.getSubmissions()} )
    },

    onFiltered(){
      return
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
</style>