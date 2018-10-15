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
            <table class="table center">
              <thead>
                <tr>
                  <th>Obligation</th>
                  <th>Reporting period</th>
                  <th>Reporting party</th>
                  <th>Version</th>
                  <th>Edit</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="submission in submissions">
                  <td>
                   {{getSumissionInfo(submission).obligation()}}
                  </td>
                  <td>
                    {{getSumissionInfo(submission).period()}}
                  </td>
                  <td>
                    {{getSumissionInfo(submission).party()}}
                  </td>
                  <td>{{submission.version}}</td>
                 <td>
                    <!-- <b-btn class="mt-1" variant="primary" v-if="!submission.editable">Open form</b-btn> -->
                  <router-link
                      class="nav-link btn btn-primary btn-sm"
                      :to="{ name: 'Form'}"
                    >
                    form
                  </router-link>
                 </td>
                </tr>
              </tbody>
            </table>
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
      }
    }
  },

  created(){

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

  methods: {
    addSubmission() {
      createSubmission(this.current)
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