<template>
  <div class="navbar-toggler-wrapper">
    <AsideToggler/>
    <span v-if="hasAssideMenu" class="toggler-text">
      <span v-if="!validationButton" v-translate>
         Add substances
      </span>
      <span v-else v-translate>
        Validation
      </span>
      </span>
  </div>
</template>

<script>
import { AsideToggler } from '@coreui/vue'

export default {
  components: {
    AsideToggler
  },
  props: {
    hasAssideMenu: Boolean,
    validationButton: null
  }
}
</script>
