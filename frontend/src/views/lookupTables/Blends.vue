<template>
  <div class="app flex-row align-items-center responsive">
	<b-container fluid>
	<b-card>
		<template slot="header">
			<b-row>
				<b-col>
                    <b-input-group prepend="Search">
                      <b-form-input v-model="table.filters.search" placeholder="Type to Search" />
                    </b-input-group>
                </b-col>
				<b-col>
                    <b-input-group>
						<multiselect
							:max-height="250"
							style="max-width:290px; max-height:50px;"
							:multiple="true"
							:clear-on-select="false"
							:hide-selected="true"
							:close-on-select="false"
							label="text"
							trackBy="value"
							placeholder="Components"
							v-model="table.filters.selectedComponentsNames"
							:options="searchComponentOptions"> </multiselect>
						<b-input-group-append>
							<b-btn  variant="primary" :disabled="!table.filters.selectedComponentsNames.length" @click="toggleIsComponentsSortDirectionDesc">
								Sort
								<i v-if="!table.filters.isComponentsSortDirectionDesc" class="fa fa-arrow-up"></i>
								<i v-if="table.filters.isComponentsSortDirectionDesc" class="fa fa-arrow-down"></i>
							</b-btn>
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
                       bordered
                       hover
						class="width-50-percent"
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
				<template slot="other_names" slot-scope="data">
					<span v-if="data.item.other_names">{{data.item.other_names}}</span>
					<span v-else>-</span>
				</template>

                <template slot="components" slot-scope="row">
					<b-table show-empty
						outlined
						bordered
						hover
						small
						head-variant="light"
						stacked="md"
						:items="row.item.components"
						:fields="tableComponents.fields"
						:current-page="tableComponents.currentPage"
						:per-page="tableComponents.perPage"
						ref="table">
							<template slot="component_name" slot-scope="data">
								<div>{{data.item.component_name}}</div>
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
import './styles.css'
import Multiselect from '@/components/common/modifiedMultiselect'

const blendsCompareByComponentPercent = (blend1, blend2, componentName, isDescending) => {
	const { percentage: componentPercentageInBlend1 } = blend1.components.find(component => component.component_name === componentName)
	const { percentage: componentPercentageInBlend2 } = blend2.components.find(component => component.component_name === componentName)
	if (isDescending) {
		return componentPercentageInBlend2 - componentPercentageInBlend1
	}
	return componentPercentageInBlend1 - componentPercentageInBlend2
}

export default {
	components: {
		Multiselect
	},
	data() {
		return {
			table: {
				fields: [{
					key: 'blend_id', label: 'Name', sortable: true, class: 'text-center width-200'
				}, {
					key: 'other_names', label: 'Other Names', sortable: true, class: 'text-center width-200'
				}, {
					key: 'components', label: 'Components', class: 'text-center'
				}
				],
				currentPage: 1,
				perPage: Infinity,
				totalRows: 50,
				pageOptions: [
					{ value: 10, text: '10' },
					{ value: 50, text: '50' },
					{ value: 100, text: '100' },
					{ value: Infinity, text: 'All' }
				],
				filters: {
					search: null,
					selectedComponentsNames: [],
					isComponentsSortDirectionDesc: null
				}
			},
			tableComponents: {
				fields: [
					{
						key: 'index', label: '', class: 'width-40'
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
			let visibleBlendsComputed = []
			const { blends } = this.$store.state.initialData
			const { selectedComponentsNames } = this.table.filters
			if (!blends) {
				return visibleBlendsComputed
			}
			blends.forEach(blend => {
				const blendIsVisible = !selectedComponentsNames.length
						|| selectedComponentsNames.every(selectedComponentName => blend.components.map(component => {
							this.$store.commit('setBlendComponentRowVariant', { component })
							if (selectedComponentsNames.includes(component.component_name)) {
								this.$store.commit('setBlendComponentRowVariant', { component, value: 'success' })
							}
							return component.component_name
						}).includes(selectedComponentName))

				if (blendIsVisible) {
					visibleBlendsComputed.push(blend)
				}
			})

			if (this.table.filters.isComponentsSortDirectionDesc !== null && this.table.filters.selectedComponentsNames.length) {
				visibleBlendsComputed = visibleBlendsComputed.sort((blend1, blend2) => blendsCompareByComponentPercent(blend1, blend2, this.table.filters.selectedComponentsNames[0], this.table.filters.isComponentsSortDirectionDesc))
			}

			return visibleBlendsComputed
		}
	},
	methods: {
		onFiltered(filteredItems) {
			this.table.totalRows = filteredItems.length
			this.table.currentPage = 1
			if (!this.table.filters.selectedComponentsNames.length) {
				this.table.filters.isComponentsSortDirectionDesc = null
			}
		},
		toggleIsComponentsSortDirectionDesc() {
			this.table.filters.isComponentsSortDirectionDesc = !this.table.filters.isComponentsSortDirectionDesc
		}
	},
	created() {
		this.$store.dispatch('getCustomBlends')
		this.$store.commit('updateBreadcrumbs', ['Lookup tables', 'Blends'])
	}
}
</script>
