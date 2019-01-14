/* eslint-disable no-tabs */
<template>
	<div v-if="section && tabName" class="validation-tab">
		<div v-for="(field, field_index) in section" :key="field_index">
			<div
				:class="{hovered: (section.indexOf(field)) === hovered }"
				class="validation-item"
				v-for="(error,error_index) in field.validation"
				:key="error_index">
				<span class="btn-link" @click="$emit('fillSearch', {substance: display.substances[field.substance]})" v-if="display.substances[field.substance]">
					{{display.substances[field.substance]}}
				</span>
				<span class="btn-link"  @click="$emit('fillSearch', {blend: display.blends[field.blend].name})" v-if="display.blends[field.blend]">
					{{display.blends[field.blend].name}}
				</span>
				<span class="btn-link"  @click="$emit('fillSearch', {facility: field.facility_name})" v-if="field.facility_name">
					{{field.facility_name}}
				</span>
				<span v-if="countryField(field)"> - {{countryField(field)}}</span>
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

	methods: {
		countryField(field) {
			const countryFields = ['source_party', 'destination_party', 'trade_party']
			const currentCountryField = Object.keys(field).find(f => field[f] && countryFields.includes(f))
			return this.display.countries[field[currentCountryField]]
		}
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
.btn-link {
	cursor: pointer;
}
</style>
