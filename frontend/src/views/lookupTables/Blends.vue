<template>
  <div class="app flex-row align-items-center">
	<b-container fluid>
	<b-card>
		<template slot="header">
			<b-row>
				<b-col>Blends</b-col>
				<b-col>
                    <b-input-group prepend="Search">
                      <b-form-input v-model="table.filters.search" placeholder="Type to Search" />
                      <b-input-group-append>
                        <b-btn variant="primary" :disabled="!table.filters.search" @click="table.filters.search = ''">Clear</b-btn>
                      </b-input-group-append>
                    </b-input-group>
                </b-col>
				<b-col>
                    <b-input-group>
						<multiselect :max-height="250" :multiple="true" :clear-on-select="false" :hide-selected="true" :close-on-select="false" label="text" trackBy="value" placeholder="Components" v-model="table.filters.selectedComponentsNames" :options="searchComponentOptions"></multiselect>
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
                       bordered
                       hover
                       head-variant="light"
                       stacked="md"
                       :items="visibleBlends"
                       :fields="table.fields"
                       :current-page="table.currentPage"
                       :per-page="table.perPage"
                       :sort-by.sync="table.sortBy"
                       :sort-desc.sync="table.sortDesc"
                       :sort-direction="table.sortDirection"
                       :filter="table.filters.search"
                       @filtered="onFiltered"
                       ref="table">
				<template slot="index" slot-scope="data">
					{{data.index + 1}}.
				</template>
                <template slot="components" slot-scope="row">
					<b-table show-empty
                       outlined
                       bordered
                       hover
                       head-variant="light"
                       stacked="md"
                       :items="row.item.components"
                       :fields="tableComponents.fields"
                       :current-page="tableComponents.currentPage"
                       :per-page="tableComponents.perPage"
                       :sort-by.sync="tableComponents.sortBy"
                       :sort-desc.sync="tableComponents.sortDesc"
                       :sort-direction="tableComponents.sortDirection"
                       ref="table">
						<template slot="index" slot-scope="data">
							{{data.index + 1}}.
						</template>
						<template slot="component_name" slot-scope="data">
							<div :class="{'border border-primary': table.filters.selectedComponentsNames.includes(data.item.component_name)}">{{data.item.component_name}}</div>
						</template>
					</b-table>
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
import Multiselect from '@/mixins/modifiedMultiselect'

export default {
	components: {
		Multiselect
	},
	data() {
		return {
			table: {
				fields: [{
					key: 'index', label: ''
				}, {
					key: 'blend_id', label: 'Name', sortable: true, class: 'text-center'
				}, {
					key: 'other_names', label: 'Other Names', sortable: true, class: 'text-center'
				}, {
					key: 'components', label: 'Components', class: 'text-center'
				}
				],
				currentPage: 1,
				perPage: 50,
				totalRows: 50,
				pageOptions: [
					{ value: 10, text: '10' },
					{ value: 50, text: '50' },
					{ value: 100, text: '100' },
					{ value: Infinity, text: 'All' }
				],
				filters: {
					search: null,
					selectedComponentsNames: []
				}
			},
			tableComponents: {
				fields: [
					{
						key: 'index', label: ''
					}, {
						key: 'component_name', label: 'Name', class: 'text-center'
					}, {
						key: 'percentage',
						label: 'Percentage',
						class: 'text-center',
						formatter: (value) => `${(value * 100).toFixed(2)}%`
					}
				],
				currentPage: 1,
				perPage: Infinity
			}
		}
	},
	computed: {
		searchComponentOptions() {
			const componentsAll = {}
			const { blends } = this.$store.state.initialData
			if (!blends) {
				return []
			}
			blends.forEach(blend => {
				blend.components.forEach(component => {
					componentsAll[component.component_name] = {
						value: component.component_name,
						text: component.component_name
					}
				})
			})
			return Object.values(componentsAll)
		},
		visibleBlends() {
			const visibleBlendsComputed = []
			const { blends } = this.$store.state.initialData
			if (!blends) {
				return visibleBlendsComputed
			}
			blends.forEach(blend => {
				const blendIsVisible = !this.table.filters.selectedComponentsNames.length
						|| this.table.filters.selectedComponentsNames.every(selectedComponentName => blend.components.map(component => component.component_name).includes(selectedComponentName))
				if (blendIsVisible) {
					visibleBlendsComputed.push(blend)
				}
			})
			return visibleBlendsComputed
		}
	},
	methods: {
		onFiltered(filteredItems) {
			this.table.totalRows = filteredItems.length
			this.table.currentPage = 1
		}
	},
	created() {
		this.$store.dispatch('getCustomBlends')
	}
}
</script>
