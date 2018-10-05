<template>
  <div v-if="data">
    {{data}}
  </div>
</template>

<script>
export default {


  props: {data: null},

  data () {
    return {

    }
  }
}
</script>

<style lang="css" scoped>
</style>