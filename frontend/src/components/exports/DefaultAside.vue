<template>
  <div>  
    <AsideToggler class="d-none d-lg-block" />
    <b-tabs>
      <b-tab>
        <template slot="title">
          Substances
        </template>
          <add :tabName="tabName"></add>
      </b-tab>
      <b-tab v-if="tabName !== 'has_destroyed'">
        <template slot="title">
          Blends
        </template>
          <AddBlend :tabName="tabName"></AddBlend>
      </b-tab>
      <b-tab>
        <template slot="title">
          Validation
        </template>
        <Validation :hovered="hovered" :tabName="tabName"></Validation>
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
    hovered: null,
    tabName: String,
  },
  created(){
  }
 
}
</script>
