<template>
  <div>  
    <AsideToggler class="d-none d-lg-block" />
    <b-tabs>
      <b-tab>
        <template slot="title">
          Substances
        </template>
          <add v-if="substances" :section="form.form_fields" :substances="substances"></add>
      </b-tab>
      <b-tab>
        <template slot="title">
          Blends
        </template>
          <AddBlend v-if="blends" :section="form.form_fields" :substances="substances" :blends="blends"></AddBlend>
      </b-tab>
    </b-tabs>
  </div>
</template>

<script>

import Add from './Add';
import {getImportSubstances, getExportBlends} from '../../api.js'
import {AsideToggler} from '@coreui/vue'
import AddBlend from './AddBlend'

export default {
  name: 'DefaultAside',
  components: {
    add: Add,
    AddBlend,
    AsideToggler
  },

  props: {
    form: null,
  },

  data () {
    return {
      substances: null,
      blends: null,
    }
  },


  created(){
    this.getSubstances()
  },

  methods: {
    getSubstances(){
      getImportSubstances().then((response) => {
        this.substances = response.data 
        getExportBlends().then((response) => {
          this.blends = response.data
        })
      })
    }
  },
}
</script>
