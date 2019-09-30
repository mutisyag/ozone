<template>
<div>
  <!-- {{aggregations}} -->
  <b-table
    show-empty
    :items="items"
    :fields="fields"
    bordered
    class="full-bordered prodcons-table"
  >
    <template v-slot:thead-top>
      <tr>
        <th v-for="(category, index) in tableTop" :key="index" :colspan="category.colspan">
          {{category.label}}
        </th>
      </tr>
    </template>
    <template v-slot:cell(group)="cell">
        {{$store.state.initialData.groupSubstances.find(g => g.id === cell.item.group).group_id}}
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
        }
        // {
        //   label: this.$gettext('Production allowance for BDN of Article 5 parties'),
        //   colspan: 3
        // }
      ]
    }
  },
  computed: {
    fields() {
      const fields = [
        { key: 'group', label: this.$gettext('Annex/Group') },
        { key: 'baseline_prod', label: this.$gettext('Baseline'), class: 'text-right' },
        { key: 'calculated_production', label: `${this.$gettext('Calculated')} (${this.$store.state.current_submission.reporting_period_description})`, class: 'text-right' },
        { key: 'limit_prod', label: this.$gettext('Limit'), class: 'text-right' },
        { key: 'baseline_cons', label: this.$gettext('Baseline'), class: 'text-right' },
        { key: 'calculated_consumption', label: `${this.$gettext('Calculated')} (${this.$store.state.current_submission.reporting_period_description})`, class: 'text-right' },
        { key: 'limit_cons', label: this.$gettext('Limit'), class: 'text-right' }
        // { key: 'baseline_bdn', label: this.$gettext('Baseline') },
        // { key: 'production_article_5', label: `${this.$gettext('Calculated')} (${this.$store.state.current_submission.reporting_period_description})` },
        // { key: 'limit_bdn', label: this.$gettext('Limit') }
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
