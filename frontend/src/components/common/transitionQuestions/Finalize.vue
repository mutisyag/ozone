<template>
	<div>
		<p>You are about to finalize this submission. Please check one of the options below</p>
		<hr>
		<fieldGenerator
				:fieldInfo="{index:'flag_valid', tabName: 'flags', field:'flag_valid'}"
				:disabled="$store.getters.transitionState"
				:field="validField"
				id="flag_valid">
		</fieldGenerator>
		<hr>
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
		formTabs() {
			return this.$store.state.form.tabs
		},
		validField() {
			return { ...this.formTabs.flags.form_fields.flag_valid, type: 'radio' }
		}
	},
	methods: {
	},
	watch: {

	}
}
</script>

