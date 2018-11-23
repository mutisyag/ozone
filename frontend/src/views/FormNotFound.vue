<template>
	<div>
		<center style="margin-top: 5rem;">
			<h1>Data form for this obligation is not available yet</h1>
			 <router-link
	                        class="btn btn-outline-primary"
	                        :to="{ name: 'Dashboard'} "
	                      >
	         	<h1>
	         		
	         		Go back to dashboard
	         	</h1>
	         </router-link>
		</center>
	</div>
</template>

<script>
export default {

  name: 'FormNotFound',

  data () {
    return {

    }
  }
}
</script>

<style lang="css" scoped>
</style>