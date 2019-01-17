<template>
  <div class="app flex-row align-items-top">
	<b-container fluid>
	<b-card>
		<template slot="header">
			<b-row>
				<b-col cols="4">
                    <b-input-group :prepend="$gettext('Name')">
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
import Vue from 'vue'
import './styles.css'
import CheckedImage from '@/components/common/CheckedImage'
import { dateFormat } from '@/components/common/services/languageService'

const ratificationHtmlFormatter = (ratification) => (ratification ? `${dateFormat(ratification.ratification_date, Vue.config.language)}<br/>${ratification.ratification_type}` : 'Pending')

export default {
	components: {
		CheckedImage
	},
	computed: {
		table() {
			const sortableAndTextCenter = {
				sortable: true,
				class: 'text-center'
			}
			const tableObj = {
				fields: [{
					key: 'name',
					label: this.$gettext('Name'),
					class: 'text-left width-200',
					sortable: true
				}, {
					key: 'is_eu_member',
					label: this.$gettext('EU Member'),
					...sortableAndTextCenter
				}, {
					key: 'is_article5',
					label: this.$gettext('Article 5 party'),
					...sortableAndTextCenter
				}, {
					key: 'is_high_ambient_temperature',
					label: this.$gettext('HAT'),
					...sortableAndTextCenter
				}, {
					key: 'vienna_convention',
					label: this.$gettext('Vienna Convention'),
					...sortableAndTextCenter
				}, {
					key: 'montreal_protocol',
					label: this.$gettext('Montreal Protocol'),
					...sortableAndTextCenter
				}, {
					key: 'london_amendment',
					label: this.$gettext('London Amendment'),
					...sortableAndTextCenter
				}, {
					key: 'copenhagen_amendment',
					label: this.$gettext('Copenhagen Amendment'),
					...sortableAndTextCenter
				}, {
					key: 'montreal_amendment',
					label: this.$gettext('Montreal Amendment'),
					...sortableAndTextCenter
				}, {
					key: 'beijing_amendment',
					label: this.$gettext('Beijing Amendment'),
					...sortableAndTextCenter
				}, {
					key: 'kigali_amendment',
					label: this.$gettext('Kigali Amendment'),
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
			return tableObj
		},
		parties() {
			const { partyRatifications } = this.$store.state.initialData
			if (!partyRatifications) {
				return []
			}

			const partyRatificationsDisplay = partyRatifications.map(party => {
				party.vienna_convention = ratificationHtmlFormatter(party.ratifications.find(ratification => ratification.treaty && ratification.treaty.treaty_id === 'VC'))
				party.montreal_protocol = ratificationHtmlFormatter(party.ratifications.find(ratification => ratification.treaty && ratification.treaty.treaty_id === 'MP'))
				party.london_amendment = ratificationHtmlFormatter(party.ratifications.find(ratification => ratification.treaty && ratification.treaty.treaty_id === 'LA'))
				party.copenhagen_amendment = ratificationHtmlFormatter(party.ratifications.find(ratification => ratification.treaty && ratification.treaty.treaty_id === 'CA'))
				party.montreal_amendment = ratificationHtmlFormatter(party.ratifications.find(ratification => ratification.treaty && ratification.treaty.treaty_id === 'MA'))
				party.beijing_amendment = ratificationHtmlFormatter(party.ratifications.find(ratification => ratification.treaty && ratification.treaty.treaty_id === 'BA'))
				party.kigali_amendment = ratificationHtmlFormatter(party.ratifications.find(ratification => ratification.treaty && ratification.treaty.treaty_id === 'KA'))
				party.is_eu_member = party.flags.is_eu_member
				party.is_article5 = party.flags.is_article5
				party.is_high_ambient_temperature = party.flags.is_high_ambient_temperature
				return party
			})

			return partyRatificationsDisplay
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
