<template>
  <div class="app flex-row align-items-top">
	<b-container fluid>
	<b-card>
		<template slot="header">
			<b-row>
				<b-col cols="4">
                    <b-input-group prepend="Name">
                      <b-form-input v-model="table.filters.searchName" />
                    </b-input-group>
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
						:items="parties"
						:fields="table.fields"
						:current-page="table.currentPage"
						:per-page="table.perPage"
						:filter="filterCallback"
						:sort-by.sync="table.sortBy"
						@filtered="onFiltered"
						ref="table">
				<template slot="is_eu_member" slot-scope="data">
					<CheckedImage :item="data.item.is_eu_member"/>
				</template>
				<template slot="is_article5" slot-scope="data">
					<CheckedImage :item="data.item.is_article5"/>
				</template>
				<template slot="is_high_ambient_temperature" slot-scope="data">
					<CheckedImage :item="data.item.is_high_ambient_temperature"/>
				</template>
				<template slot="vienna_convention" slot-scope="data">
					<div v-html="data.item.vienna_convention"></div>
				</template>
				<template slot="montreal_protocol" slot-scope="data">
					<div v-html="data.item.montreal_protocol"></div>
				</template>
				<template slot="london_amendment" slot-scope="data">
					<div v-html="data.item.london_amendment"></div>
				</template>
				<template slot="copenhagen_amendment" slot-scope="data">
					<div v-html="data.item.copenhagen_amendment"></div>
				</template>
				<template slot="montreal_amendment" slot-scope="data">
					<div v-html="data.item.montreal_amendment"></div>
				</template>
				<template slot="beijing_amendment" slot-scope="data">
					<div v-html="data.item.beijing_amendment"></div>
				</template>
				<template slot="kigali_amendment" slot-scope="data">
					<div v-html="data.item.kigali_amendment"></div>
				</template>
              </b-table>
          </b-card>
		</b-container>
  </div>
</template>

<script>
import './styles.css'
import CheckedImage from '@/components/common/CheckedImage'

export default {
	components: {
		CheckedImage
	},
	data() {
		const sortableAndTextCenter = {
			sortable: true,
			class: 'text-center'
		}

		return {
			table: {
				fields: [{
					key: 'name',
					label: 'Name',
					class: 'text-left width-200',
					sortable: true
				}, {
					key: 'is_eu_member',
					label: 'EU Member',
					...sortableAndTextCenter
				}, {
					key: 'is_article5',
					label: 'Article 5 party',
					...sortableAndTextCenter
				}, {
					key: 'is_high_ambient_temperature',
					label: 'HAT',
					...sortableAndTextCenter
				}, {
					key: 'vienna_convention',
					label: 'Vienna Convention',
					...sortableAndTextCenter
				}, {
					key: 'montreal_protocol',
					label: 'Montreal Protocol',
					...sortableAndTextCenter
				}, {
					key: 'london_amendment',
					label: 'London Amendment',
					...sortableAndTextCenter
				}, {
					key: 'copenhagen_amendment',
					label: 'Copenhagen Amendment',
					...sortableAndTextCenter
				}, {
					key: 'montreal_amendment',
					label: 'Montreal Amendment',
					...sortableAndTextCenter
				}, {
					key: 'beijing_amendment',
					label: 'Beijing Amendment',
					...sortableAndTextCenter
				}, {
					key: 'kigali_amendment',
					label: 'Kigali Amendment',
					...sortableAndTextCenter
				}],
				currentPage: 1,
				perPage: Infinity,
				totalRows: 50,
				sortBy: null,
				filters: {
					searchName: null
				}
			}
		}
	},
	computed: {
		parties() {
			const { partyRatifications } = this.$store.state.initialData
			if (!partyRatifications) {
				return []
			}
			return partyRatifications
		}
	},
	methods: {
		onFiltered(filteredItems) {
			this.table.totalRows = filteredItems.length
			this.table.currentPage = 1
		},
		filterCallback(party) {
			if (!this.table.filters.searchName) {
				return true
			}
			return party.name && party.name.toLowerCase().includes(this.table.filters.searchName.toLowerCase())
		}
	},
	created() {
		this.$store.dispatch('getPartyRatifications')
		this.$store.commit('updateBreadcrumbs', ['Lookup tables', 'Parties'])
	}
}
</script>
