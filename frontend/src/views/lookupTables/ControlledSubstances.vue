<template>
  <div class="app flex-row align-items-center">
	<b-container fluid>
	<b-card>
		<template slot="header">
			<b-row>
				<b-col>Controlled substances</b-col>
				<b-col>
                    <b-input-group>
						<b-input-group-prepend>
							<b-form-select :options="table.searchInColumnsOptions" value-field="key" text-field="label"  v-model="table.filters.selectedSearchInColumnOption" />
						</b-input-group-prepend>
						<b-form-input v-model="table.filters.search" placeholder="Type to Search" />
						<b-input-group-append>
							<b-btn variant="primary" :disabled="!table.filters.search" @click="table.filters.search = ''">Clear</b-btn>
                      </b-input-group-append>
                    </b-input-group>
                </b-col>
				<b-col>
                    <b-input-group>
                      <b-btn variant="primary" :disabled="!table.sortBy" @click="changeSortDefaultOrderToken">Sort default</b-btn>
                    </b-input-group>
                </b-col>
				<b-col>
					<b-input-group horizontal prepend="Per page">
						<b-form-select :options="table.pageOptions" v-model="table.perPage" />
					</b-input-group>
				</b-col>
			</b-row>
		</template>
		<b-table show-empty
						outlined
						stripped
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
				<template slot="index" slot-scope="data">
					{{data.index + 1}}.
				</template>
              </b-table>
              <b-row>
                <b-col md="6" class="my-1">
                  <b-pagination :total-rows="table.totalRows" :per-page="table.perPage" v-model="table.currentPage" class="my-0" />
                </b-col>
              </b-row>

          </b-card>
		</b-container>
  </div>
</template>

<script>
const uuidv1 = require('uuid/v1')

const fields = [{
	key: 'index', label: ''
}, {
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

export default {
	data() {
		return {
			table: {
				fields,
				currentPage: 1,
				perPage: Infinity,
				totalRows: 50,
				sortBy: 'group_id',
				sortDesc: false,
				pageOptions: [
					{ value: 10, text: '10' },
					{ value: 50, text: '50' },
					{ value: 100, text: '100' },
					{ value: Infinity, text: 'All' }
				],
				searchInColumnsOptions: [fields[1], fields[2], fields[3]],
				filters: {
					search: null,
					selectedSearchInColumnOption: fields[1].key,
					sortDefaultOrderToken: uuidv1()
				}
			}
		}
	},
	computed: {
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
			if (this.table.filters.sortDefaultOrderToken) {
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
		changeSortDefaultOrderToken() {
			this.table.sortBy = 'group_id'
			this.table.sortDesc = false
			this.table.filters.sortDefaultOrderToken = uuidv1()
		},
		filterCallback(substance) {
			const { selectedSearchInColumnOption } = this.table.filters
			if (!this.table.filters.search) {
				return true
			}
			return `${substance[selectedSearchInColumnOption]}`.toLowerCase().includes(this.table.filters.search.toLowerCase())
		}
	},
	created() {
		this.$store.dispatch('getSubstances')
	}
}
</script>
