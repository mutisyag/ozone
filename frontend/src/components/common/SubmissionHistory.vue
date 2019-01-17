<template>
	<div v-if="history">
		<b-table show-empty
				outlined
				bordered
				hover
				head-variant="light"
				stacked="md"
				:items="tableItems"
				:fields="table.fields"
				:sort-by.sync="table.sortBy"
				:sort-desc.sync="table.sortDesc"
				:sort-direction="table.sortDirection"
				ref="table"
		>
		</b-table>
	</div>
</template>

<script>
export default {
	props: {
		history: Array,
		currentVersion: Number
	},

	data() {
		return {
			table: {
				fields: [
					{
						key: 'version', label: this.$gettext('Version'), sortable: true, sortDirection: 'desc', class: 'text-center'
					},
					{
						key: 'updated_at', label: this.$gettext('Last Modified'), sortable: true, class: 'text-center'
					},
					{
						key: 'current_state', label: this.$gettext('Current State'), sortable: true, sortDirection: 'desc', class: 'text-center'
					},
					{
						key: 'flag_provisional', label: this.$gettext('Provisional'), sortable: true, sortDirection: 'desc', class: 'text-center'
					},
					{
						key: 'flag_valid', label: this.$gettext('Valid'), sortable: true, class: 'text-center'
					}
				],
				sortBy: null,
				sortDesc: false,
				sortDirection: 'asc',
				modalInfo: { title: '', content: '' }
			}
		}
	},

	computed: {
		tableItems() {
			const tableFields = []
			this.history.forEach((element) => {
				tableFields.push({
					version: element.version,
					updated_at: element.updated_at,
					current_state: element.current_state,
					flag_provisional: element.flag_provisional,
					flag_valid: element.flag_valid,
					// Highlight the version that is currently viewed.
					_rowVariant: this.currentVersion === element.version ? 'info' : ''
				})
			})
			return tableFields
		}
	}
}
</script>

<style lang="css" scoped>
</style>
