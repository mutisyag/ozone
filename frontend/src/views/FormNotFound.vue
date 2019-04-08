<template>
	<div>
		<center style="margin-top: 5rem;">
			<h1>
				<span v-translate>Data form for this obligation is not available yet</span>
			</h1>
			<router-link class="btn btn-outline-primary" :to="{ name: 'Dashboard'}">
				<h1>
					<span v-translate>Go back to dashboard</span>
				</h1>
			</router-link>
		</center>
	</div>
</template>

<script>
export default {
  name: 'FormNotFound',
  data() {
    return {

    }
  }
}
</script>

<style lang="css" scoped>
</style>
