<template>
  <div class="app flex-row align-items-center">
	<b-container fluid>
	<b-card>
		<template slot="header">
			<b-row>
				<b-col cols="4">
                    <b-input-group prepend="Search">
                      <b-form-input v-model="table.filters.search" placeholder="Type to Search" />
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
						:items="parties"
						:fields="table.fields"
						:current-page="table.currentPage"
						:per-page="table.perPage"
						:filter="table.filters.search"
						:sort-by.sync="table.sortBy"
						@filtered="onFiltered"
						ref="table">
				<template slot="is_eu_member" slot-scope="data">
					<CheckedImage :item="data.item.is_eu_member"/>
				</template>
				<template slot="is_a5" slot-scope="data">
					<CheckedImage :item="data.item.is_a5"/>
				</template>
				<template slot="is_high_ambient_temperature" slot-scope="data">
					<CheckedImage :item="data.item.is_high_ambient_temperature"/>
				</template>
              </b-table>
          </b-card>
		</b-container>
  </div>
</template>

<script>
import './styles.css'
import uuidv1 from 'uuid/v1'
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
		const sortableAndTextCenterAndRatificationDateFormatter = {
			...sortableAndTextCenter,
			formatter: (value) => (value ? `${value.ratification_date} \n ${value.ratification_type}` : '-')
		}

		return {
			table: {
				fields: [{
					key: 'name',
					label: 'Name',
					...sortableAndTextCenter
				}, {
					key: 'is_eu_member',
					label: 'EU Member',
					...sortableAndTextCenter
				}, {
					key: 'is_a5',
					label: 'Article 5 party',
					...sortableAndTextCenter
				}, {
					key: 'is_high_ambient_temperature',
					label: 'HAT',
					...sortableAndTextCenter
				}, {
					key: 'vienna_convention',
					label: 'Vienna Convention',
					...sortableAndTextCenterAndRatificationDateFormatter
				}, {
					key: 'montreal_protocol',
					label: 'Montreal Protocol',
					...sortableAndTextCenterAndRatificationDateFormatter
				}, {
					key: 'london_amendment',
					label: 'London Amendment',
					...sortableAndTextCenterAndRatificationDateFormatter
				}, {
					key: 'copenhagen_amendment',
					label: 'Copenhagen Amendment',
					...sortableAndTextCenterAndRatificationDateFormatter
				}, {
					key: 'montreal_amendment',
					label: 'Montreal Amendment',
					...sortableAndTextCenterAndRatificationDateFormatter
				}, {
					key: 'beijing_amendment',
					label: 'Beijing Amendment',
					...sortableAndTextCenterAndRatificationDateFormatter
				}, {
					key: 'kigali_amendment',
					label: 'Kigali Amendment',
					...sortableAndTextCenterAndRatificationDateFormatter
				}],
				currentPage: 1,
				perPage: Infinity,
				totalRows: 50,
				sortBy: null,
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
				return []
			}
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
