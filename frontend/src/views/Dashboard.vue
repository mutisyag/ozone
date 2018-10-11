<template>
	<div> 
		<router-link
          class="nav-link"
          :to="{ name: 'Form'}"
        >
        form
        </router-link>
	</div>
</template>

<script>
export default {

  name: 'Dashboard',

  data () {
    return {

    }
  }
}
</script>

<style lang="css" scoped>
</style>