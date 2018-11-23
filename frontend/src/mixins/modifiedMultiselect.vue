<template>
  <multiselect
    v-bind="$attrs"
    v-on="forwardListeners"
    v-model="completeValue"
    :options="options"
    :track-by="trackBy"
  >
  </multiselect>
</template>
<script>
import Multiselect from 'vue-multiselect'

export default {
  inheritAttrs: false,
  components: {
    Multiselect
  },
  props: ['value', 'options', 'trackBy'],
  computed: {
    completeValue: {
      get () {
        console.log(this.value)
        return this.$attrs['multiple']
          ? this.value ? this.value.map(value => this.findOption(value)) : null
          : this.findOption(this.value)
      },
      set (v) {
        this.$emit('input', this.$attrs['multiple']
          ? v.map(value => value[this.trackBy])
          : (v && v[this.trackBy])
        )
      }
    },
    forwardListeners () {
      const {input, ...listeners} = this.$listeners
      return listeners
    }
  },
  methods: {
    findOption (value) {
      return this.options.find(option => option[this.trackBy] === value)
    }
  }
}
</script>