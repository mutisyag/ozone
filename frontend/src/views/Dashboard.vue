<template>
  <div class="animated fadeIn">
    <b-row>
      <b-col sm="6">
        <b-card>
          <div slot="header">
            <strong>Latest submissions </strong>
          </div>
          <div>
          <router-link
            class="nav-link btn btn-primary"
            :to="{ name: 'Form'}"
          >
          form
          </router-link>

          <div v-if="submissions && submissions.length">{{submissions}}</div>

          </div>
        </b-card>
      </b-col>
      <b-col sm="6">
        <b-card>
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
      periods: [],
      obligations: [],
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
    let countryOptions = []
      for (let country of response.data) {
        countryOptions.push({ value: country.abbr, text: country.name})
      }
      this.parties = countryOptions
    })

    getPeriods().then( response => {
      for(let period of response.data) {
        this.periods.push({value: period.id, text: `${period.name} (${period.start_date} - ${period.end_date})`})
      }
    })

    getObligations().then( response => {
      for(let obligation of response.data) {
        this.obligations.push({value: obligation.id, text: obligation.name})
      }
    })

  },

  methods: {
    addSubmission() {
      let party_pk;
      for(let party of this.parties) {
        if(this.current.party === party.value){
          party_pk = this.parties.indexOf(party)
          console.log('partyppk',party_pk)
          break;
        }
      }

      this.current.party = party_pk
      createSubmission(this.current)
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