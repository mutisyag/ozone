<template>
	<div class="validation-tab">
		<div v-for="field in section">
			{{field.validation.selected}}
		</div>
	</div>
</template>

<script>
export default {

	props: {
		section: Array
	},

  name: 'Validation',

  data () {
    return {

    }
  }
}
</script>

<style lang="css" scoped>
</style>