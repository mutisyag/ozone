<template>
  <div>  
    <AsideToggler class="d-none d-lg-block" />
    <b-tabs>
      <b-tab>
        <template slot="title">
          Substances
        </template>
          <add :countryOptions="data.countryOptions" :section="form.form_fields" :substances="data.substances"></add>
      </b-tab>
      <b-tab>
        <template slot="title">
          Blends
        </template>
          <AddBlend :countryOptions="data.countryOptions"  :section="form.form_fields" :substances="data.substances" :blends="data.blends"></AddBlend>
      </b-tab>
    </b-tabs>
  </div>
</template>

<script>

import Add from './Add';
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
    data: null,
  },
 
}
</script>
