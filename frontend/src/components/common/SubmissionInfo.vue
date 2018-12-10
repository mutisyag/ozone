<template>
  <div v-if="info">
    <b-row>
      <b-col>
        <b-input-group size="sm" :prepend="info.party.label">
          <b-form-input :name="info.party.name" :value="$store.state.initialData.display.countries[$store.state.current_submission.party]" :type="info.party.type" :disabled="info.party.disabled"></b-form-input>
        </b-input-group>
      </b-col>

      <b-col>
        <b-input-group size="sm" :prepend="info.reporting_year.label">
          <b-form-input :name="info.reporting_year.name" :value="$store.state.current_submission.reporting_period" :type="info.reporting_year.type" :disabled="info.reporting_year.disabled"></b-form-input>
        </b-input-group>
      </b-col>
    </b-row>

    <small>
       {{info.intro}}
    </small>
    <!-- <h2>{{info.title}}</h2> -->

    <form class="form-sections">
      <b-card>
        <div class="form-fields" v-for="field in info.form_fields" :key="field.name">
          <b-row class="field-wrapper">
            <b-col lg='3'>
              <label><b>{{field.label}}</b></label>
            </b-col>
            <b-col>
              <fieldGenerator :fieldInfo="{index:info.form_fields.indexOf(field), tabName: info.name, field:field.name}" :disabled="$store.getters.transitionState" :field="field"></fieldGenerator>
            </b-col>
          </b-row>

        </div>
      </b-card>
    </form>

    </div>
</template>

<script>

import fieldGenerator from '@/components/common/form-components/fieldGenerator'

export default {

	name: 'Tab1',

	props: {
		info: Object,
		tabs: Object
	},

	created() {
		// this.tabs.push('asd')
	},

	components: { fieldGenerator },

	data() {
		return {

		}
	},

	methods: {
	}

}
</script>

<style lang="css" scoped>

</style>
