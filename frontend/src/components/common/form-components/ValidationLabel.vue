<template>
    <i
      style="cursor:pointer; color:red;"
      variant="danger"
      class="fa fa-exclamation-circle fa-lg"
      @click="openValidationCallback"
      v-if="validation.length"
      v-b-tooltip.hover
      title="Click here to see the validation problems"
    ></i>
</template>

<script>
import { getCommonLabels } from '@/components/common/dataDefinitions/labels'

export default {
  props: {
    openValidationCallback: Function,
    validation: Array
  },

  created() {
    this.labels = getCommonLabels(this.$gettext)
  },

  components: { },

  data() {
    return {
      labels: null
    }
  },

  methods: {
  }

}
</script>
