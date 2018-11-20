<template>
	<div v-if="section && tabName" class="validation-tab">
		
		<div v-for="field in section">
			<div :class="{hovered: (section.indexOf(field)) === hovered }" class="validation-item" v-for="error in field.validation.selected">
				{{display.substances[field.substance.selected]}}{{display.blends[field.blend.selected] ? display.blends[field.blend.selected].name : null }} - <span style="color: red">{{error}}</span>
			</div>
		</div>
	</div>
</template>

<script>
export default {

	props: {
		tabName: String,
		hovered: null,
	},

	computed:{
		section(){ return this.$store.getters.getValidationForCurrentTab(this.tabName) },
		display(){ return this.$store.state.initialData.display}
	},

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