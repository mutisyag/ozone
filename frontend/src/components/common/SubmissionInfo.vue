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
				<b-col cols="8">
					<h5><span v-translate>Submission Info</span></h5>
					<b-card>
						<div class="form-fields">
							<b-row :id="order" v-for="order in info.fields_order" class="field-wrapper" :key="order">
								<b-col lg='3'>
									<span v-if="info.form_fields[order].tooltip" v-b-tooltip.hover placement="left" :title="info.form_fields[order].tooltip">
										<i class="fa fa-info-circle fa-lg"></i>&nbsp;
										<label>{{labels[order]}}
										</label>
									</span>
									<span v-else>
										<b-badge class="floating-error" v-if="info.form_fields[order].validation" variant="danger" v-translate>Required</b-badge>
										<label>{{labels[order]}}</label>
									</span>
								</b-col>
								<b-col>
									<fieldGenerator :fieldInfo="{index:order, tabName: info.name, field:order}" :disabled="order === 'reporting_channel' ? !$store.getters.can_change_reporting_channel : !$store.getters.can_edit_data" :field="info.form_fields[order]"></fieldGenerator>
								</b-col>
							</b-row>
						</div>
					</b-card>
				</b-col>

				<b-col v-if="flags_info">
					<h5><span v-translate>Flags</span></h5>
					<b-card id="flags">
						<b-row>
							<b-col>
								<b-row v-for="order in general_flags" :key="order">
									<b-col cols="1">
										<fieldGenerator
											:fieldInfo="{index:order, tabName: flags_info.name, field:order}"
											:disabled="$store.getters.transitionState"
											:field="flags_info.form_fields[order]"
											:id="order">
										</fieldGenerator>
									</b-col>
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
								</b-row>
							</b-col>
							<b-col>
								<b-row v-for="order in blank_flags" :key="order">
									<b-col cols="1">
										<fieldGenerator
											:fieldInfo="{index:order, tabName: flags_info.name, field:order}"
											:disabled="$store.getters.transitionState"
											:field="flags_info.form_fields[order]"
											:id="order">
										</fieldGenerator>
									</b-col>
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
								</b-row>
							</b-col>
						</b-row>
						<div>
							<h5 class="mt-4 mb-4" v-translate>Annex group reported in full</h5>
								<b-row id="annex-flags">
									<b-col sm="12" md="2" lg="2" v-for="column in specific_flags_columns" :key="column">
										<div class="specific-flags-wrapper" v-if="order.split('_')[3].includes(column)" v-for="order in specific_flags" :key="order">
											<span cols="1">
												<fieldGenerator
													:fieldInfo="{index:order, tabName: flags_info.name, field:order}"
													:disabled="$store.getters.transitionState"
													:field="flags_info.form_fields[order]"
													:id="order">
												</fieldGenerator>
											</span>
											<span>
												<label :class="{'muted': flags_info.form_fields[order].disabled}" :for="order">
													<div v-if="flags_info.form_fields[order].tooltip" v-b-tooltip.hover placement="left" :title="flags_info.form_fields[order].tooltip">
														<i class="fa fa-info-circle fa-lg"></i>
														{{labels.flags[order]}}
													</div>
													<div v-else>
														{{labels.flags[order]}}
													</div>
												</label>
											</span>
										</div>
								</b-col>
								</b-row>

						</div>
					</b-card>
				</b-col>
			</b-row>
    </form>
    </div>
</template>

<script>

import fieldGenerator from '@/components/common/form-components/fieldGenerator'
import { getCommonLabels } from '@/components/common/dataDefinitions/labels'
import { dateFormat } from '@/components/common/services/languageService'

export default {
	props: {
		info: Object,
		flags_info: Object
	},

	created() {
		this.labels = getCommonLabels(this.$gettext)
	},

	components: { fieldGenerator },

	computed: {

		general_flags() {
			return ['flag_provisional', 'flag_superseded', 'flag_valid']
		},

		blank_flags() {
			return Object.keys(this.flags_info.form_fields).filter(f => f.split('_').includes('blanks'))
		},

		specific_flags() {
			return Object.keys(this.flags_info.form_fields).filter(f => ![...this.general_flags, ...this.blank_flags].includes(f))
		},

		specific_flags_columns() {
			return [...new Set(this.specific_flags.map(f => f.split('_')[3]).map(f => f.split('')[0]))]
		},
		currentSubmissionSubmittedAt() {
			const { submitted_at } = this.$store.state.current_submission
			if (!submitted_at) {
				return null
			}
			return dateFormat(submitted_at, this.$language.current)
		}
	},

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
