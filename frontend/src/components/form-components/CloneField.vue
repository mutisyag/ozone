<template>
  <div v-if="field && tabName">
    <div class="container">
      <div style="position: relative">
          <multiselect :max-height="250" :multiple="true" :clear-on-select="false" :hide-selected="true" :close-on-select="false" label="text" trackBy="value" placeholder="Countries" v-model="selected_countries.selected" :options="countryOptions"></multiselect>
          <b-btn @click="addSubstance" v-if="selected_countries.selected.length">Add</b-btn>
      </div>
    </div>
  </div>
</template>
<script>

// import Multiselect from 'vue-multiselect'
import Multiselect from '@/mixins/modifiedMultiselect'

export default {

	props: {
		tabName: String,
		current_field: Object
	},

	components: {
		Multiselect
	},

	created() {
		this.field = JSON.parse(JSON.stringify(this.current_field))
	},

	computed: {
		countryOptions() {
			if (this.tabName === 'has_nonparty') {
				return this.$store.state.initialData.countryOptions.filter(country => this.$store.state.initialData.nonParties[this.current_field.group.selected][country.value])
			}
			return this.$store.state.initialData.countryOptions
		}
	},

	data() {
		return {
			field: null,
			selected_countries: {
				selected: []
			}
		}
	},

	methods: {

		addSubstance() {
			const current_field = JSON.parse(JSON.stringify(this.field))
			const typeOfCountryFields = ['destination_party', 'source_party', 'trade_party']
			let currentTypeOfCountryField = ''
			const willNotAdd = []

			typeOfCountryFields.forEach(type => {
				if (current_field.hasOwnProperty(type)) currentTypeOfCountryField = type
			})

			this.selected_countries.selected.forEach(country => {
				let fieldExists = false
				for (const existing_field of this.$store.state.form.tabs[this.tabName].form_fields) {
					if (current_field.substance.selected) {
						if (existing_field.substance.selected === current_field.substance.selected && existing_field[currentTypeOfCountryField].selected === country) {
							fieldExists = true
							willNotAdd.push(country)
							break
						}
					} else if (current_field.blend.selected) {
						if (existing_field.blend.selected === current_field.blend.selected && existing_field[currentTypeOfCountryField].selected === country) {
							fieldExists = true
							willNotAdd.push(country)
							break
						}
					}
				}
				// substanceList, currentSectionName, groupName, currentSection, country, blend, prefillData
				if (!fieldExists) {
					this.$store.dispatch('createSubstance', {
						substanceList: [current_field.substance.selected],
						currentSectionName: this.tabName,
						groupName: current_field.group.selected,
						country,
						blendList: [current_field.blend.selected],
						prefillData: null
					})
				} else {
					const willNotAddCountryNames = []
					willNotAdd.forEach(countryId => {
						const { text } = this.countryOptions.find(countryDisplay => countryDisplay.value === countryId)
						if (text) {
							willNotAddCountryNames.push(text)
						}
					})
					this.$store.dispatch('setAlert', {
						message: { __all__: [`The fields for the folllowing countries: ${willNotAddCountryNames.join(', ')} were not added because they already exist`] },
						variant: 'danger'
					})
				}
			})

			this.$emit('removeThisField')
			this.resetData()
		},

		resetData() {
			this.selected_countries.selected = []
		},

		removeSpecialChars(str) {
			return str.replace(/[^a-zA-Z0-9]+/g, '')
		}
	},
	watch: {
		current_field: {
			handler() {
				this.field = JSON.parse(JSON.stringify(this.current_field))
			}
		}
	}
}
</script>

<style lang="css" scoped>
</style>
