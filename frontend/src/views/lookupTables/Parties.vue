<template>
  <div class="app flex-row align-items-center">
	<b-container fluid>
	<b-card>
		<template slot="header">
			<b-row>
				<b-col>Parties</b-col>
				<b-col>
                    <b-input-group prepend="Search">
                      <b-form-input v-model="table.filters.search" placeholder="Type to Search" />
                      <b-input-group-append>
                        <b-btn variant="primary" :disabled="!table.filters.search" @click="table.filters.search = ''">Clear</b-btn>
                      </b-input-group-append>
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
						class="width-70-percent"
						head-variant="light"
						stacked="md"
						:items="parties"
						:fields="table.fields"
						:current-page="table.currentPage"
						:per-page="table.perPage"
						:filter="table.filters.search"
						:sort-by.sync="table.sortBy"
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
import './styles.css'
import uuidv1 from 'uuid/v1'

export default {
	data() {
		return {
			table: {
				fields: [{
					key: 'index', label: '', class: 'width-40'
				}, {
					key: 'name', label: 'Name', sortable: true, class: 'text-center'
				}, {
					key: 'abbr', label: 'Abbr', sortable: true, class: 'text-center'
				}, {
					key: 'subregion', label: 'Subregion', sortable: true, class: 'text-center'
				}],
				currentPage: 1,
				perPage: Infinity,
				totalRows: 50,
				sortBy: null,
				pageOptions: [
					{ value: 10, text: '10' },
					{ value: 50, text: '50' },
					{ value: 100, text: '100' },
					{ value: Infinity, text: 'All' }
				],
				filters: {
					search: null,
					sortDefaultOrderToken: uuidv1()
				}
			}
		}
	},
	computed: {
		parties() {
			const { partyRatifications } = this.$store.state.initialData
			if (!partyRatifications) {
				console.log(this.$store.state.initialData)
				return []
			}
			console.log(partyRatifications)
			return partyRatifications
		}
	},
	methods: {
		onFiltered(filteredItems) {
			this.table.totalRows = filteredItems.length
			this.table.currentPage = 1
		}
	},
	created() {
		this.$store.dispatch('getPartyRatifications')
	}
}
</script>
