<template>
  <div class="app blends-lookup-table flex-row align-items-top">
    <div class="w-100 pt-3">

      <!-- Filters -->
      <b-row>
        <b-col v-for="(filterValue, filterKey) in filters" :key="filterKey">
          <b-input-group horizontal :prepend="$gettext(filterValue.name)" class="mb-1">
            <b-form-select v-model="selectedFilters[filterKey]">
              <option :value="null" selected></option>
              <option
                v-for="option in filterValue.options"
                :value="option.id"
                :key="option.id"
              >{{option.name || option.group_id}}</option>
            </b-form-select>
          </b-input-group>
        </b-col>
        <b-col md="1">
          <b-input-group-append>
            <b-btn id="blends-clear-button" variant="light" @click="onResetFilters">
              <span v-translate>Clear</span>
            </b-btn>
          </b-input-group-append>
        </b-col>
      </b-row>

      <!-- Table -->
      <b-table
        show-empty
        outlined
        bordered
        hover
        head-variant="light"
        stacked="md"
        :items="filteredItems"
        :fields="fields"
        :sort-by.sync="sortBy"
        :per-page="tableOptions.params.page_size"
        ref="table"
        @sort-changed="sortings"
      ></b-table>

      <b-row>
        <b-col md="10" class="my-1">
          <b-pagination
            :total-rows="tableOptions.totalRows"
            :per-page="tableOptions.params.page_size"
            v-model="tableOptions.params.page"
            class="my-0"
          />
        </b-col>
        <b-col md="2">
          <b-input-group horizontal :prepend="$gettext('Per page')" class="mb-0">
            <b-form-select
              :options="tableOptions.pageOptions"
              v-model="tableOptions.params.page_size"
            />
          </b-input-group>
        </b-col>
      </b-row>
    </div>
  </div>
</template>

<script>
import { getLimits, getPeriods, getSubstances, getParties } from '@/components/common/services/api.js'

export default {
  data() {
    return {
      fields: [
        { key: 'party', label: `${this.$gettext('Party')}`, sortable: true },
        { key: 'group', label: `${this.$gettext('Annex/Group')}`, sortable: true },
        { key: 'reporting_period', label: `${this.$gettext('Reporting period')}`, sortable: true },
        { key: 'limit_type', label: `${this.$gettext('Limit type')}`, sortable: false },
        { key: 'limit', label: `${this.$gettext('Limit')}`, sortable: false },
        { key: 'reported_value', label: `${this.$gettext('Reported')}`, sortable: false },
        { key: 'baseline_value', label: `${this.$gettext('Baseline')}`, sortable: false }
      ],
      items: [],
      filters: {
        party: { name: 'Party', options: [], call: getParties },
        group: { name: 'Annex/Group', options: [], call: getSubstances },
        reporting_period: { name: 'Reporting period', options: [], call: getPeriods }
      },
      selectedFilters: {
        party: null,
        group: null,
        reporting_period: null
      },
      sortBy: null,
      tableOptions: {
        pageOptions: [10, 25, 100],
        totalRows: 0,
        params: {
          page_size: 10,
          page: null,
          party: null,
          reporting_period: null,
          group: null,
          ordering: null
        }
      }
    }
  },
  computed: {
    filteredItems: function filterItems() {
      const tempItems = this.items.slice()
      const result = tempItems.map(item => {
        for (const itemKey in item) {
          const filter = this.filters[itemKey]

          if (filter) {
            const optionItem = filter.options.find(option => option.id === item[itemKey])
            const optionName = optionItem.name || optionItem.group_id

            item[itemKey] = optionName
          }
        }
        return item
      })
      return result
    }
  },
  methods: {
    makeFilters() {
      const allPromises = []

      for (const filterName in this.filters) {
        const p = new Promise((resolve, reject) => {
          this.filters[filterName].call().then((response) => {
            resolve({ filterName, response })
          })
        })
        allPromises.push(p)
      }

      Promise.all(allPromises).then((responses) => {
        for (const responseItem of responses) {
          this.filters[responseItem.filterName].options = responseItem.response.data.slice()
        }
      })
    },
    getItems() {
      getLimits(this.tableOptions.params).then((response) => {
        this.items = response.data.results.slice()
        this.tableOptions.totalRows = response.data.count
      })
    },
    sortings(el) {
      this.tableOptions.params.ordering = el.sortDesc ? `-${el.sortBy}` : el.sortBy
      this.getItems()
    },
    onResetFilters() {
      const currentFilters = JSON.parse(JSON.stringify(this.selectedFilters))
      for (const filter in currentFilters) {
        currentFilters[filter] = null
      }
      this.selectedFilters = currentFilters
      this.sortBy = null
      this.tableOptions.params.ordering = null
    },
    updateBreadcrumbs() {
      this.$store.commit('updateBreadcrumbs', this.$gettext('Consumption'))
    }
  },

  created() {
    this.getItems()
    this.makeFilters()
    this.updateBreadcrumbs()
  },

  watch: {
    'selectedFilters': {
      handler() {
        this.tableOptions.params = { ...this.tableOptions.params, ...this.selectedFilters }
        this.tableOptions.params.page = null
        this.getItems()
      },
      deep: true
    },
    'tableOptions.params.page': {
      handler() {
        this.getItems()
      }
    },
    'tableOptions.params.page_size': {
      handler() {
        this.tableOptions.params.page = null
        this.getItems()
      }
    },
    '$language.current': {
      handler() {
        this.updateBreadcrumbs()
      }
    }
  }
}
</script>

<style>
</style>
