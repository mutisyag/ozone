<template>
  <div class="app lookup-tables-page flex-row align-items-top">
    <div class="w-100 pt-3">

      <b-row class="mb-2">
        <b-col cols="4">
          <b-input-group :prepend="$gettext('Search')">
            <b-form-input id="parties-name-filter" v-model="table.filters.searchName"/>
          </b-input-group>
        </b-col>
      </b-row>
      <b-table
        show-empty
        striped
        outlined
        class="full-bordered"
        bordered
        :sort-compare="sortCompare"
        hover
        head-variant="light"
        stacked="md"
        :items="parties"
        :fields="tableFields"
        :current-page="table.currentPage"
        :per-page="table.perPage"
        :filter="table.filters.searchName"
        :sort-by.sync="table.sortBy"
        @filtered="onFiltered"
        ref="table"
      >
        <template v-slot:thead-top>
          <tr>
            <th colspan="5">&nbsp;</th>
            <th colspan="7" class="text-center"><span v-translate>Ratification details</span></th>
          </tr>
        </template>
        <template v-slot:cell(is_eu_member)="data">
          <CheckedImage :item="data.item.is_eu_member"/>
        </template>
        <template v-slot:cell(is_article5)="data">
          <CheckedImage :item="data.item.is_article5"/>
        </template>
        <template v-slot:cell(is_group2)="data">
          <CheckedImage :item="data.item.is_group2"/>
        </template>
        <template v-slot:cell(is_high_ambient_temperature)="data">
          <CheckedImage :item="data.item.is_high_ambient_temperature"/>
        </template>
        <template v-slot:cell(vienna_convention)="data">
          <div v-html="data.item.vienna_convention"></div>
        </template>
        <template v-slot:cell(montreal_protocol)="data">
          <div v-html="data.item.montreal_protocol"></div>
        </template>
        <template v-slot:cell(london_amendment)="data">
          <div v-html="data.item.london_amendment"></div>
        </template>
        <template v-slot:cell(copenhagen_amendment)="data">
          <div v-html="data.item.copenhagen_amendment"></div>
        </template>
        <template v-slot:cell(montreal_amendment)="data">
          <div v-html="data.item.montreal_amendment"></div>
        </template>
        <template v-slot:cell(beijing_amendment)="data">
          <div v-html="data.item.beijing_amendment"></div>
        </template>
        <template v-slot:cell(kigali_amendment)="data">
          <div v-html="data.item.kigali_amendment"></div>
        </template>
      </b-table>
    </div>
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
        key: 'is_group2',
        label: this.$gettext('Group 2'),
        ...sortableAndTextCenter
      }, {
        key: 'is_high_ambient_temperature',
        label: this.$gettext('HAT'),
        ...sortableAndTextCenter
      }, {
        key: 'vienna_convention',
        label: `${this.$gettext('Vienna Convention')} (${this.parties.filter(p => p.vienna_convention).length})`,
        ...sortableAndTextCenter
      }, {
        key: 'montreal_protocol',
        label: `${this.$gettext('Montreal Protocol')} (${this.parties.filter(p => p.montreal_protocol).length})`,
        ...sortableAndTextCenter
      }, {
        key: 'london_amendment',
        label: `${this.$gettext('London Amendment')} (${this.parties.filter(p => p.london_amendment).length})`,
        ...sortableAndTextCenter
      }, {
        key: 'copenhagen_amendment',
        label: `${this.$gettext('Copenhagen Amendment')} (${this.parties.filter(p => p.copenhagen_amendment).length})`,
        ...sortableAndTextCenter
      }, {
        key: 'montreal_amendment',
        label: `${this.$gettext('Montreal Amendment')} (${this.parties.filter(p => p.montreal_amendment).length})`,
        ...sortableAndTextCenter
      }, {
        key: 'beijing_amendment',
        label: `${this.$gettext('Beijing Amendment')} (${this.parties.filter(p => p.beijing_amendment).length})`,
        ...sortableAndTextCenter
      }, {
        key: 'kigali_amendment',
        label: `${this.$gettext('Kigali Amendment')} (${this.parties.filter(p => p.kigali_amendment).length})`,
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
        party.is_group2 = party.flags.is_group2
        party.is_high_ambient_temperature = party.flags.is_high_ambient_temperature
        return party
      })

      return partyRatificationsDisplay
    }
  },
  methods: {
    updateBreadcrumbs() {
      this.$store.commit('updateBreadcrumbs', `${this.$gettext('Parties')} | ${this.$gettext('Online Reporting System')}`)
    },
    onFiltered(filteredItems) {
      this.table.totalRows = filteredItems.length
      this.table.currentPage = 1
    },
    sortCompare(a, b, key, direction) {
      const placeholder = direction ? '1000' : '3000'
      const sortByDateType = ['london_amendment', 'montreal_protocol', 'copenhagen_amendment', 'montreal_amendment', 'beijing_amendment', 'kigali_amendment', 'montreal_protocol', 'vienna_convention']
      if (sortByDateType.includes(key)) {
        const first = a[key] !== undefined ? new Date(a[key].split('<br/>')[0]) : new Date(placeholder)
        const second = b[key] !== undefined ? new Date(b[key].split('<br/>')[0]) : new Date(placeholder)
        if (first > second) {
          return 1
        }
        if (first < second) {
          return -1
        }
        if (first === second) {
          return 0
        }
      }
      return null
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
    this.updateBreadcrumbs()
  }
}
</script>
