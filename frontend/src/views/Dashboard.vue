<template>
  <div class="animated fadeIn">
    <b-row>
      <b-col sm="6">
        <b-card>
          <div slot="header">
            <strong>Form </strong>
          </div>
          <div>
          <router-link
            class="nav-link btn btn-primary"
            :to="{ name: 'Form'}"
          >
          form
          </router-link>

          </div>
        </b-card>
      </b-col>
      <b-col sm="6">
        <b-card>
          <div slot="header">
            <strong>Submissions </strong><small>Form</small>
          </div>
          <div>{{submissions}}</div>
        </b-card>
      </b-col>
    </b-row>
  </div>
</template>

<script>

import {getSubmissions} from '@/api/api';

export default {
  name: 'Dashboard',
  data () {
    return {
    	submissions: null
    }
  },

  created(){
  	getSubmissions().then( response => {
  		this.submissions = response.data
  	} )
  },

  methods: {
    click () {
      // do nothing
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
</style>