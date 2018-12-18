/* eslint-disable no-tabs */
<template>
	<div v-if="section && tabName" class="validation-tab">
		<div v-for="(field, field_index) in section" :key="field_index">
			<div
				:class="{hovered: (section.indexOf(field)) === hovered }"
				class="validation-item"
				v-for="(error,error_index) in field.validation"
				:key="error_index">
				<span v-if="display.substances[field.substance]">
					{{display.substances[field.substance]}}
				</span>
				<span v-if="display.blends[field.blend]">
					{{display.blends[field.blend].name}}
				</span>
				<span v-if="field.facility_name">
					{{field.facility_name}}
				</span>
				- <span style="color: red">{{error}}</span>
			</div>
		</div>
	</div>
</template>

<script>
export default {

	props: {
		tabName: String,
		hovered: null
	},

	computed: {
		section() { return this.$store.getters.getValidationForCurrentTab(this.tabName) },
		display() { return this.$store.state.initialData.display }
	},

	data() {
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
