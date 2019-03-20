<template>
	<div>
		<div>
			<div v-if="provisional">
				<p>Kindly note that the data being submitted is marked as provisional. Another report will need to be submitted with the final data.</p>
				<hr>
			</div>
			<div v-else>
				<p>You are about to submit your report.</p>
				<hr>
			</div>
			<div v-if="questionnaireStatus.length">
				<p>You have chosen "Yes" in the questionnaire, but not entered any substances in {{questionnaireStatus.join(', ')}} form</p>
				<hr>
			</div>
			<div v-if="uncheckedFlags.length">
				<p>Kindly note that all substances not included in the reporting forms are considered zero.</p>
				<p>You have not reported data for annex group: {{uncheckedFlags.join(', ')}}</p>
				<hr>
			</div>
		</div>
		<div v-if="$store.state.currentUser.is_secretariat">
			<b-row v-for="order in blank_flags" :key="order">
				<b-col cols="1">
					<fieldGenerator
						:fieldInfo="{index:order, tabName: 'flags', field:order}"
						:disabled="$store.getters.transitionState"
						:field="formTabs.flags.form_fields[order]"
						:id="order">
					</fieldGenerator>
				</b-col>
				<b-col>
					<label :class="{'muted': formTabs.flags.form_fields[order].disabled}" :for="order">
						<div v-if="formTabs.flags.form_fields[order].tooltip" v-b-tooltip.hover placement="left" :title="formTabs.flags.form_fields[order].tooltip">
							<i class="fa fa-info-circle fa-lg"></i>
							{{labels.flags[order]}}
						</div>
						<div v-else>
							{{labels.flags[order]}}
						</div>
					</label>
				</b-col>
			</b-row>
			<hr>
		</div>
		<p>Press OK to continue with the submission. Press Cancel to make further changes or corrections.</p>

	</div>
</template>

<script>
import fieldGenerator from '@/components/common/form-components/fieldGenerator'
import { getCommonLabels } from '@/components/common/dataDefinitions/labels'

export default {
	data() {
		return {
			labels: null
		}
	},
	created() {
		this.labels = getCommonLabels(this.$gettext)
	},
	components: {
		fieldGenerator
	},
	computed: {
		provisional() {
			return this.$store.state.form.tabs.flags.form_fields.flag_provisional.selected
		},
		blank_flags() {
			return Object.keys(this.formTabs.flags.form_fields).filter(f => this.formTabs.flags.fields_order.includes(f) && f !== 'validation' && f.split('_').includes('blanks'))
		},
		questionnaire() {
			return this.$store.state.form.tabs.questionaire_questions
		},
		formTabs() {
			return this.$store.state.form.tabs
		},
		questionnaireStatus() {
			if (!this.questionnaire) {
				return []
			}
			const answeredYes = Object.keys(this.questionnaire.form_fields).filter(q => this.questionnaire.form_fields[q].selected)
			const anweredYesNoData = Object.keys(this.formTabs).filter(tab => answeredYes.includes(tab) && !this.formTabs[tab].form_fields.length)
			return anweredYesNoData
		},
		uncheckedFlags() {
			return Object.keys(this.formTabs.flags.form_fields).filter(flag => flag.includes('flag_has_reported') && !this.formTabs.flags.form_fields[flag].selected)
		}
	},
	methods: {
	},
	watch: {

	}
}
</script>

