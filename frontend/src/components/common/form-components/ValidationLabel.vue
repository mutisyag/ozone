<template>
    <i
      style="cursor:pointer; color:red;"
      variant="danger"
      class="fa fa-exclamation-circle fa-lg"
      @click="openValidationCallback(index)"
      v-if="validation.length"
      v-b-tooltip.hover
      tabindex="0"
      title="Click here to see the validation problems"
    ></i>
</template>

<script>
import { getCommonLabels } from '@/components/common/dataDefinitions/labels'

export default {
  props: {
    openValidationCallback: Function,
    validation: Array,
    index: Number
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
