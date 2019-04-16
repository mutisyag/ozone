<template>
<div>
  <!-- {{aggregations}} -->
  <b-table
    show-empty
    striped
    hover
    :items="items"
    :fields="fields"
    bordered
  >
    <template slot="thead-top">
      <tr>
        <th v-for="(category, index) in tableTop" :key="index" :colspan="category.colspan">
          {{category.label}}
        </th>
      </tr>
    </template>
    <template slot="group" slot-scope="cell">
        {{$store.state.initialData.groupSubstances[cell.value].group_id}}
    </template>
  </b-table>
</div>
</template>
<script>
export default {
  props: {
    aggregations: Array,
    standalone: Boolean
  },
  data() {
    return {
      tableTop: [
        { label: '' }, {
          label: this.$gettext('Production'),
          colspan: 3
        }, {
          label: this.$gettext('Consumption'),
          colspan: 3
        }, {
          label: this.$gettext('BDN Article 5'),
          colspan: 3
        }
      ]
    }
  },
  computed: {
    fields() {
      const fields = [
        { key: 'group', label: this.$gettext('Annex/Group') },
        { key: 'baseline_prod', label: this.$gettext('Baseline') },
        { key: 'calculated_production', label: `${this.$gettext('Calculated')} (${this.$store.state.current_submission.reporting_period})` },
        { key: 'limit_prod', label: this.$gettext('Limit') },
        { key: 'baseline_cons', label: this.$gettext('Baseline') },
        { key: 'calculated_consumption', label: `${this.$gettext('Calculated')} (${this.$store.state.current_submission.reporting_period})` },
        { key: 'limit_cons', label: this.$gettext('Limit') },
        { key: 'baseline_bdn', label: this.$gettext('Baseline') },
        { key: 'production_article_5', label: `${this.$gettext('Calculated')} (${this.$store.state.current_submission.reporting_period})` },
        { key: 'limit_bdn', label: this.$gettext('Limit') }
      ]
      return fields
    },
    items() {
      return this.aggregations
    }
  }
}
</script>
<style scoped>
  table thead tr:first-of-type th{
    text-align: center;
  }
</style>
