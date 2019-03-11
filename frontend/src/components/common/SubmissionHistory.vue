<template>
	<div v-if="history && obligations">
		<b-table show-empty
				outlined
				bordered
				hover
				head-variant="light"
				stacked="md"
				:items="tableItems"
        :fields="tableFields"
				:sort-by.sync="table.sortBy"
				:sort-desc.sync="table.sortDesc"
				:sort-direction="table.sortDirection"
				ref="table"
		>
			<template slot="actions" slot-scope="cell">
							<a
									@click="changeRoute({ name: getFormName(cell.item.details.obligation), query: {submission: cell.item.actions}})"
									class="btn btn-outline-primary btn-sm"
									>
								<span v-translate>View</span>
							</a>
			</template>
		</b-table>
	</div>
</template>

<script>
import { getObligations } from '@/components/common/services/api'

export default {
	props: {
		history: Array,
		currentVersion: Number
	},

	created() {
		this.getObligations()
	},
	data() {
		return {
			obligations: null,
			table: {
				sortBy: null,
				sortDesc: false,
				sortDirection: 'asc',
				modalInfo: { title: '', content: '' }
			}
		}
	},

	methods: {
		changeRoute({ name, query }) {
			this.$router.push({ name, query: { submission: query.submission } })
			this.$router.go(this.$router.currentRoute)
		},
		getFormName(obligation) {
			return this.obligations.find(o => o.id === obligation).form_type
		},
		async getObligations() {
			const obligations = await getObligations()
			this.obligations = obligations.data
		}
	},

	computed: {
		tableItems() {
			const tableFields = []
			this.history.forEach((element) => {
				tableFields.push({
					version: element.version,
					created_by: element.filled_by_secretariat ? 'Secretariat' : 'Party',
					updated_at: element.updated_at,
					current_state: element.current_state,
					actions: element.url,
					details: element,
					_rowVariant: this.currentVersion === element.version ? 'info' : ''
				})
			})
			return tableFields
		},
		tableFields() {
			return [
				{
					key: 'version', label: this.$gettext('Version'), sortable: true, sortDirection: 'desc', class: 'text-center'
				},
				{
					key: 'created_by', label: this.$gettext('Created by'), sortable: true, class: 'text-center'
				},
				{
					key: 'updated_at', label: this.$gettext('Last Modified'), sortable: true, class: 'text-center'
				},
				{
					key: 'current_state', label: this.$gettext('Current State'), sortable: true, sortDirection: 'desc', class: 'text-center'
				},
				{
					key: 'actions', label: this.$gettext('Actions')
				}
			]
		}
	}
}
</script>

<style lang="css" scoped>
</style>
