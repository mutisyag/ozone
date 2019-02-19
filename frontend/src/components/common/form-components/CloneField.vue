<template>
  <div v-if="field && tabName">
    <div class="container">
      <div style="position: relative">
          <multiselect
			:max-height="250"
			:multiple="true"
			:clear-on-select="false"
			:hide-selected="true"
			:close-on-select="false"
			:disabled="disabled"
			label="text"
			trackBy="value"
			:placeholder="$gettext('Countries')"
			v-model="selected_countries.selected"
			:options="countryOptions" />
			<b-btn @click="addSubstance" variant="primary" class="mt-1" size="sm" v-if="selected_countries.selected.length">
				<span v-translate='{length: selected_countries.selected.length}'>Add %{length} rows</span>
			</b-btn>
      </div>
    </div>
  </div>
</template>
<script>

import Multiselect from '@/components/common/ModifiedMultiselect'

export default {

	props: {
		tabName: String,
		current_field: Object,
		disabled: Boolean
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
						if (parseInt(existing_field.substance.selected) === parseInt(current_field.substance.selected) && parseInt(existing_field[currentTypeOfCountryField].selected) === parseInt(country)) {
							fieldExists = true
							willNotAdd.push(country)
							break
						}
					} else if (current_field.blend.selected) {
						if (parseInt(existing_field.blend.selected) === parseInt(current_field.blend.selected) && parseInt(existing_field[currentTypeOfCountryField].selected) === parseInt(country)) {
							fieldExists = true
							willNotAdd.push(country)
							break
						}
					}
				}
				// substanceList, currentSectionName, groupName, currentSection, country, blend, prefillData
				if (!fieldExists) {
					this.$store.dispatch('createSubstance', {
						$gettext: this.$gettext,
						substanceList: [current_field.substance.selected],
						currentSectionName: this.tabName,
						groupName: current_field.group.selected,
						country,
						blendList: [current_field.blend.selected],
						prefillData: null
					})
				}
			})
			const willNotAddCountryNames = []
			willNotAdd.length && willNotAdd.forEach(countryId => {
				const { text } = this.countryOptions.find(countryDisplay => countryDisplay.value === countryId)
				if (text) {
					willNotAddCountryNames.push(text)
				}
			})
			willNotAddCountryNames.length && this.$store.dispatch('setAlert', {
				$gettext: this.$gettext,
				message: { __all__: [`${this.$gettext('The fields for these countries were not added because they already exist')} : ${willNotAddCountryNames.join(', ')}}`] },
				variant: 'danger'
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
