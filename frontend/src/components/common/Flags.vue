<template>
<b-card>
	<b-row v-for="order in tab.fields_order" :key="order">
		<b-col cols="2">
			<label :for="order">
				{{labels[order]}}
			</label>
		</b-col>
		<b-col>
			<fieldGenerator
				:fieldInfo="{index:order, tabName: tab.name, field:order}"
				:disabled="$store.getters.transitionState"
				:field="tab.form_fields[order]"
				:id="order">
			</fieldGenerator>
		</b-col>

	</b-row>
</b-card>
</template>
<script>

import fieldGenerator from '@/components/common/form-components/fieldGenerator'
import labels from '@/components/common/dataDefinitions/labels'

export default {
	name: 'Flags',

	components: {
		fieldGenerator
	},

	created() {
		this.labels = labels.flags
	},

	data() {
		return {
			labels: null
		}
	},

	props: {
		tab: null
	}
}
</script>

