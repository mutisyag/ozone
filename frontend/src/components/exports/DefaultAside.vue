<template>
  <div>  
    <AsideToggler class="d-none d-lg-block" />
    <b-tabs>
      <b-tab>
        <template slot="title">
          Substances
        </template>
          <add :countryOptions="data.countryOptions" :currentSection="form.name" :section="form.form_fields" :substances="data.substances"></add>
      </b-tab>
      <b-tab>
        <template slot="title">
          Blends
        </template>
          <AddBlend :countryOptions="data.countryOptions" :display="data.display"  :currentSection="form.name" :section="form.form_fields" :substances="data.substances" :blends="data.blends"></AddBlend>
      </b-tab>
      <b-tab>
        <template slot="title">
          Validation
        </template>
        <Validation :hovered="hovered" :display="data.display" :section="form.form_fields"></Validation>
      </b-tab>
    </b-tabs>
  </div>
</template>

<script>

import Add from './Add';
import {AsideToggler} from '@coreui/vue'
import AddBlend from './AddBlend'
import Validation from './Validation'

export default {
  name: 'DefaultAside',
  components: {
    add: Add,
    AddBlend,
    AsideToggler,
    Validation
  },

  props: {
    form: null,
    data: null,
    hovered: null,
  },
  created(){
  }
 
}
</script>
