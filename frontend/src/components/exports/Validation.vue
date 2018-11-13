<template>
	<div v-if="section && display" class="validation-tab">
		<div v-for="field in section">
			<div :class="{hovered: (field.substance.selected || field.blend.selected) === hovered }" class="validation-item" v-for="error in field.validation.selected">
				{{display.substances[field.substance.selected]}}{{display.blends[field.blend.selected] ? display.blends[field.blend.selected].name : null }} - <span style="color: red">{{error}}</span>
			</div>
		</div>
	</div>
</template>

<script>
export default {

	props: {
		section: Array,
		display: Object,
		hovered: null,
	},

  name: 'Validation',

  data () {
    return {

    }
  }
}
</script>

<style lang="css" scoped>
.validation-tab {
	padding: 1rem;
}

.validation-item {
	border: 1px solid transparent;
	padding: .5rem;
}

.hovered {
	border-color: red;
}
</style>