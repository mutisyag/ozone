<template>
  <div class="navbar-toggler-wrapper">
    <AsideToggler/>
    <span v-if="hasAssideMenu" class="toggler-text" v-translate>Add substances</span>
  </div>
</template>

<script>
import { AsideToggler } from '@coreui/vue'

export default {
  components: {
    AsideToggler
  },
  props: {
    hasAssideMenu: Boolean
  }
}
</script>
