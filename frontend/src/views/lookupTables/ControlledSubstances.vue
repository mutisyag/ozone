<template>
  <div class="app flex-row align-items-top">
    <b-card style="width: 100%">
      <template slot="header">
        <strong v-translate>Controlled substances</strong>
      </template>
      <b-row class="mb-2">
        <b-col>
          <b-input-group :prepend="$gettext('Group')">
            <b-form-input id="substances-group-filter" v-model="table.filters.searchGroup"/>
          </b-input-group>
        </b-col>
        <b-col>
          <b-input-group :prepend="$gettext('Name')">
            <b-form-input id="substances-name-filter" v-model="table.filters.searchName"/>
          </b-input-group>
        </b-col>
        <b-col>
          <b-input-group :prepend="$gettext('Formula')">
            <b-form-input id="substances-formula-filter" v-model="table.filters.searchFormula"/>
          </b-input-group>
        </b-col>
        <b-col>
          <b-input-group-append>
            <b-btn
              id="substances-clear-button"
              variant="light"
              :disabled="isDisabledClearFilters"
              @click="clearFilters"
            >
              <span v-translate>Clear</span>
            </b-btn>
          </b-input-group-append>
        </b-col>
      </b-row>
      <b-table
        show-empty
        outlined
        striped
        bordered
        hover
        head-variant="light"
        stacked="md"
        :items="substances"
        :fields="tableFields"
        :current-page="table.currentPage"
        :per-page="table.perPage"
        :filter="table.filters"
        :filter-function="filterCallback"
        :sort-by.sync="table.sortBy"
        :sort-desc.sync="table.sortDesc"
        @filtered="onFiltered"
        ref="table"
      ></b-table>
    </b-card>
  </div>
</template>

<script>
import './styles.css'

export default {
  data() {
    return {
      table: {
        currentPage: 1,
        perPage: Infinity,
        sortBy: 'group_id',
        sortDesc: false,
        filters: {
          searchGroup: null,
          searchName: null,
          searchFormula: null
        }
      }
    }
  },
  computed: {
    tableFields() {
      return [
        {
          key: 'annex',
          label: this.$gettext('Annex'),
          sortable: true,
          class: 'text-center'
        },
        {
          key: 'group_id',
          label: this.$gettext('Group'),
          sortable: true,
          class: 'text-center'
        },
        {
          key: 'name',
          label: this.$gettext('Name'),
          sortable: true,
          class: 'text-center'
        },
        {
          key: 'odp',
          label: this.$gettext('ODP'),
          sortable: true,
          class: 'text-center'
        },
        {
          key: 'formula',
          label: this.$gettext('Formula'),
          sortable: true,
          class: 'text-center'
        },
        {
          key: 'number_of_isomers',
          label: this.$gettext('Number of Isomers'),
          sortable: true,
          class: 'text-center'
        },
        {
          key: 'min_odp',
          label: this.$gettext('MinODP'),
          sortable: true,
          class: 'text-center'
        },
        {
          key: 'max_odp',
          label: this.$gettext('MaxODP'),
          sortable: true,
          class: 'text-center'
        }
      ]
    },
    isDisabledClearFilters() {
      const { filters } = this.table
      return (
        !filters.searchGroup && !filters.searchName && !filters.searchFormula
      )
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
        substances = [
          ...substances,
          ...groupSubstance.substances.map(substance => ({
            ...substance,
            group_id,
            annex: group_id[0]
          }))
        ]
      })
      if (this.isDisabledClearFilters) {
        substances = substances.sort((a, b) => a.sort_order - b.sort_order)
      }
      return substances
    }
  },
  methods: {
    updateBreadcrumbs() {
      this.$store.commit('updateBreadcrumbs', this.$gettext('Lookup tables for controlled substances'))
    },
    onFiltered(filteredItems) {
      this.table.totalRows = filteredItems.length
      this.table.currentPage = 1
    },
    filterCallback(substance) {
      const { filters } = this.table
      if (filters.searchGroup) {
        if (
          !substance.group_id || !substance.group_id.toLowerCase().includes(filters.searchGroup.toLowerCase())) {
          return false
        }
      }
      if (filters.searchName) {
        if (!substance.name || !substance.name.toLowerCase().includes(filters.searchName.toLowerCase())) {
          return false
        }
      }
      if (filters.searchFormula) {
        if (
          !substance.formula || !substance.formula.toLowerCase().includes(filters.searchFormula.toLowerCase())) {
          return false
        }
      }
      return true
    },
    clearFilters() {
      const { filters } = this.table
      filters.searchGroup = null
      filters.searchName = null
      filters.searchFormula = null
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
    this.$store.dispatch('getSubstances')
  }
}
</script>
