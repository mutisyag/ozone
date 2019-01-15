<template>
  <div>
    <AsideToggler/>
		<b-tabs v-model="tabIndex">
      <b-tab v-if="hasSubstances">
        <template slot="title">
          <span v-translate>Substances</span>
        </template>
          <add :tabName="tabName"></add>
      </b-tab>
      <b-tab v-if="hasBlends">
        <template slot="title">
          <span v-translate>Blends</span>
        </template>
          <AddBlend :tabName="tabName"></AddBlend>
      </b-tab>
      <b-tab :title-link-class="validationLength > 0 ? {} : null">
        <template slot="title">
          <span v-translate>Validation</span> <b-badge v-if="validationLength" variant="danger">{{validationLength}}</b-badge>
        </template>
        <Validation v-on:fillSearch="$emit('fillSearch', $event)" :hovered="hovered" :tabName="tabName"></Validation>
      </b-tab>
    </b-tabs>
		<div class="legend">
			<b><span v-translate>Legend:</span></b>
			<div>
				<div class="spinner">
					<div class="loader"></div>
				</div> - <span v-translate>Form is curently being saved</span>
			</div>
			<div>
				<i style="color: red;" class="fa fa-times-circle fa-lg"></i> - <span v-translate>Form save failed. Please check the validation</span>
			</div>
			<div>
				<i style="color: green;" class="fa fa-check-circle fa-lg"></i> - <span v-translate>Form was saved or no modifications were made. Current form data is synced with the data on the server</span>
			</div>
			<div>
				<i class="fa fa-edit fa-lg"></i> - <span v-translate>The form was edited and the data is not yet saved on the server. Please save before closing the form</span>
			</div>
    </div>
  </div>
</template>

<script>

import { AsideToggler } from '@coreui/vue'
import Add from './Add'
import AddBlend from './AddBlend'
import Validation from './Validation'

export default {
	name: 'DefaultAside',
	components: {
		add: Add,
		AddBlend,
		AsideToggler,
		Validation
	},

	data() {
		return {
			tabIndex: 0
		}
	},

	computed: {
		hasSubstances() {
			return Object.keys(this.$store.state.form.tabs[this.tabName].default_properties).includes('substance')
		},
		hasBlends() {
			return Object.keys(this.$store.state.form.tabs[this.tabName].default_properties).includes('blend')
		},
		validationLength() {
			return this.$store.getters.getValidationForCurrentTab(this.tabName).filter(field => field.validation.length).length
		}
	},

	props: {
		hovered: null,
		tabName: String,
		parentTabIndex: Number
	},

	watch: {
		parentTabIndex: {
			handler(new_val) {
				if (new_val !== this.tabIndex) {
					console.log(new_val)
					this.tabIndex = new_val
				}
			}
		},
		tabIndex: {
			handler(new_val) {
				if (new_val !== this.parentTabIndex) {
					this.$emit('update:parentTabIndex', new_val)
				}
			}
		}
	}

}
</script>
<style scoped>
.legend {
  padding: .2rem 2rem;
  background: #f0f3f5;
}

.legend .loader {
	animation: unset;
}

.legend .spinner {
  margin-left: 0;
}
</style>
