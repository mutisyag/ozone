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
		<hr>
    <form class="form-sections">
			<b-row>
				<b-col>
					<h5><span v-translate>Submission Info</span></h5>
					<b-card>
						<div class="form-fields">
							<b-row v-for="order in info.fields_order" class="field-wrapper" :key="order">
								<b-col lg='3'>
									<label>{{labels[order]}}</label>
								</b-col>
								<b-col>
									<fieldGenerator :fieldInfo="{index:order, tabName: info.name, field:order}" :disabled="$store.getters.transitionState" :field="info.form_fields[order]"></fieldGenerator>
								</b-col>
							</b-row>
							<b-row>
								<b-col lg='3'>
									<label>{{labels.dateOfSubmission}}</label>
								</b-col>
								<b-col>
									<span v-if="$store.state.current_submission.submitted_at">{{$store.state.current_submission.submitted_at}}</span>
									<i v-else class="fa fa-ellipsis-h"></i>
								</b-col>
							</b-row>
						</div>
					</b-card>
				</b-col>

				<b-col v-if="flags_info">
					<h5><span v-translate>Flags</span></h5>
					<b-card>
						<b-row v-for="order in flags_info.fields_order" :key="order">
							<b-col>
								<label :class="{'muted': flags_info.form_fields[order].disabled}" :for="order">
									<div v-if="flags_info.form_fields[order].tooltip" v-b-tooltip.hover placement="left" :title="flags_info.form_fields[order].tooltip">
										<i class="fa fa-info-circle fa-lg"></i>
										{{labels.flags[order]}}
									</div>
									<div v-else>
										{{labels.flags[order]}}
									</div>
								</label>
							</b-col>
							<b-col>
								<fieldGenerator
									:fieldInfo="{index:order, tabName: flags_info.name, field:order}"
									:disabled="$store.getters.transitionState"
									:field="flags_info.form_fields[order]"
									:id="order">
								</fieldGenerator>
							</b-col>

						</b-row>
					</b-card>
				</b-col>
			</b-row>
    </form>
    </div>
</template>

<script>

import fieldGenerator from '@/components/common/form-components/fieldGenerator'
import { getCommonLabels } from '@/components/common/dataDefinitions/labels'

export default {
	props: {
		info: Object,
		flags_info: Object
	},

	created() {
		this.labels = getCommonLabels(this.$gettext)
	},

	components: { fieldGenerator },

	data() {
		return {
			labels: null
		}
	},

	methods: {
	},
	watch: {
		'$language.current': {
			handler() {
				this.labels = getCommonLabels(this.$gettext)
			}
		}
	}

}
</script>
