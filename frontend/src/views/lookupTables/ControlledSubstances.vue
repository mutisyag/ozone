<template>
  <div class="app flex-row align-items-top">
	<b-container fluid>
	<b-card>
		<template slot="header">
			<b-row>
				<b-col>
                    <b-input-group prepend="Group">
                      <b-form-input v-model="table.filters.searchGroup"/>
                    </b-input-group>
                </b-col>
				<b-col>
                    <b-input-group prepend="Name">
                      <b-form-input v-model="table.filters.searchName"/>
                    </b-input-group>
                </b-col>
				<b-col>
                    <b-input-group prepend="ODP">
                      <b-form-input v-model="table.filters.searchODP" type="number"/>
                    </b-input-group>
                </b-col>
				<b-col>
                    <b-input-group-append>
                      <b-btn variant="primary" :disabled="isDisabledClearFilters" @click="clearFilters">Clear</b-btn>
                    </b-input-group-append>
                </b-col>
			</b-row>
		</template>
		<b-table show-empty
						outlined
						striped
						bordered
						hover
						head-variant="light"
						stacked="md"
						:items="substances"
						:fields="table.fields"
						:current-page="table.currentPage"
						:per-page="table.perPage"
						:filter="filterCallback"
						:sort-by.sync="table.sortBy"
						:sort-desc.sync="table.sortDesc"
						@filtered="onFiltered"
						ref="table">
              </b-table>
			</b-card>
		</b-container>
  </div>
</template>

<script>
import './styles.css'

export default {
	data() {
		const fields = [{
			key: 'annex', label: 'Annex', sortable: true, class: 'text-center'
		}, {
			key: 'group_id', label: 'Group', sortable: true, class: 'text-center'
		}, {
			key: 'name', label: 'Name', sortable: true, class: 'text-center'
		}, {
			key: 'odp', label: 'ODP', sortable: true, class: 'text-center'
		}, {
			key: 'formula', label: 'Formula', sortable: true, class: 'text-center'
		}, {
			key: 'number_of_isomers', label: 'Number of Isomers', sortable: true, class: 'text-center'
		}, {
			key: 'min_odp', label: 'MinODP', sortable: true, class: 'text-center'
		}, {
			key: 'max_odp', label: 'MaxODP', sortable: true, class: 'text-center'
		}]

		return {
			table: {
				fields,
				currentPage: 1,
				perPage: Infinity,
				totalRows: 50,
				sortBy: 'group_id',
				sortDesc: false,
				filters: {
					searchGroup: null,
					searchName: null,
					searchODP: null
				}
			}
		}
	},
	computed: {
		isDisabledClearFilters() {
			const { filters } = this.table
			return !filters.searchGroup && !filters.searchName && !filters.searchODP
		},
		substances() {
			let substances = []
			const { groupSubstances } = this.$store.state.initialData
			if (!groupSubstances) {
				return substances
			}
			groupSubstances.forEach(groupSubstance => {
				if (!groupSubstance.substances || !groupSubstance.substances.length) {
					return
				}
				const { group_id } = groupSubstance
				substances = [...substances,
					...groupSubstance.substances
						.map(substance => ({
							...substance,
							group_id,
							annex: group_id[0]
						}))]
			})
			if (this.isDisabledClearFilters) {
				substances = substances.sort((a, b) => a.sort_order - b.sort_order)
			}
			return substances
		}
	},
	methods: {
		onFiltered(filteredItems) {
			this.table.totalRows = filteredItems.length
			this.table.currentPage = 1
		},
		filterCallback(substance) {
			const { filters } = this.table
			if (filters.searchGroup) {
				if (!substance.group_id || !substance.group_id.toLowerCase().includes(filters.searchGroup.toLowerCase())) {
					return false
				}
			}
			if (filters.searchName) {
				if (!substance.name || !substance.name.toLowerCase().includes(filters.searchName.toLowerCase())) {
					return false
				}
			}
			if (filters.searchODP) {
				if (!substance.odp
					|| (substance.odp !== parseFloat(filters.searchODP) && !`${substance.odp}`.startsWith(filters.searchODP))) {
					return false
				}
			}
			return true
		},
		clearFilters() {
			const { filters } = this.table
			filters.searchGroup = null
			filters.searchName = null
			filters.searchODP = null
		}
	},
	created() {
		this.$store.dispatch('getSubstances')
		this.$store.commit('updateBreadcrumbs', ['Lookup tables', 'Controlled substances'])
	}
}
</script>
