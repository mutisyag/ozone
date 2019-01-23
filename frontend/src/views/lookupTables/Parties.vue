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
						:fields="tableFields"
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
import { dateFormat } from '@/components/common/services/languageService'

const formatRatificationHtml = (ratification, language) => (ratification ? `${dateFormat(ratification.ratification_date, language)}<br/>${ratification.ratification_type}` : 'Pending')

export default {
	components: {
		CheckedImage
	},
	data() {
		return {
			table: {
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
		tableFields() {
			const sortableAndTextCenter = {
				sortable: true,
				class: 'text-center'
			}
			return [{
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
			}]
		},
		parties() {
			const { partyRatifications } = this.$store.state.initialData
			if (!partyRatifications) {
				return []
			}

			const partyRatificationsDisplay = partyRatifications.map(party => {
				party.ratifications.forEach(ratification => {
					if (!ratification.treaty) {
						return
					}
					const ratificationHtml = formatRatificationHtml(ratification, this.$language.current)
					switch (ratification.treaty.treaty_id) {
					case 'VC':
						party.vienna_convention = ratificationHtml
						break
					case 'MP':
						party.montreal_protocol = ratificationHtml
						break
					case 'LA':
						party.london_amendment = ratificationHtml
						break
					case 'CA':
						party.copenhagen_amendment = ratificationHtml
						break
					case 'MA':
						party.montreal_amendment = ratificationHtml
						break
					case 'BA':
						party.beijing_amendment = ratificationHtml
						break
					case 'KA':
						party.kigali_amendment = ratificationHtml
						break
					default:
						break
					}
				})

				party.is_eu_member = party.flags.is_eu_member
				party.is_article5 = party.flags.is_article5
				party.is_high_ambient_temperature = party.flags.is_high_ambient_temperature
				return party
			})

			return partyRatificationsDisplay
		}
	},
	methods: {
		updateBreadcrumbs() {
			this.$store.commit('updateBreadcrumbs', [this.$gettext('Lookup tables'), this.$gettext('Parties')])
		},
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
	watch: {
		'$language.current': {
			handler() {
				this.updateBreadcrumbs()
			}
		}
	},
	created() {
		const body = document.querySelector('body')
		if (body.classList.contains('aside-menu-lg-show')) {
			document.querySelector('body').classList.remove('aside-menu-lg-show')
		}
		this.$store.dispatch('getPartyRatifications')
	}
}
</script>
