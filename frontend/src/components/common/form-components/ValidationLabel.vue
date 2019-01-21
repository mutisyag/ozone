<template>
<span class="validation-wrapper">
	<b-badge
		pill
		style="cursor:pointer"
		variant="danger"
		@click="openValidationCallback"
		v-if="validation.length"
		v-b-tooltip.hover
		title="Click here to see the validation problems">
			{{labels.invalid}}
	</b-badge>
	<b-badge v-else pill variant="success">{{labels.valid}}</b-badge>
</span>
</template>

<script>
import { getCommonLabels } from '@/components/common/dataDefinitions/labels'

export default {
	props: {
		openValidationCallback: Function,
		validation: Array
	},

	created() {
		this.labels = getCommonLabels(this.$gettext)
	},

	components: { },

	data() {
		return {
			labels: null
		}
	},

	methods: {
	}

}
</script>
