<template>
  <div>
    <b-btn class="square-right" @click="getAggregations()" variant="outline-dark" v-translate>Calculated amounts</b-btn>
    <b-modal id="aggregationModal" size="xl" ref="aggregationModal">
      <div slot="modal-title">
        <span v-translate>Calculated production and consumption</span> - {{ $store.state.initialData.display.countries[$store.state.current_submission.party] }} - {{ $store.state.current_submission.reporting_period }}
      </div>
      <AggregationsTable :standalone="false" :aggregations="aggregations"></AggregationsTable>
      <div slot="modal-footer">
        <b-btn @click="$refs.aggregationModal.hide()" variant="success" v-translate>Close</b-btn>
      </div>
    </b-modal>
  </div>
</template>
<script>

import { getSubmissionAggregations } from '@/components/common/services/api'
import AggregationsTable from '@/components/common/AggregationsTable'

export default {
  props: {
    submission: String
  },
  components: {
    AggregationsTable
  },
  data() {
    return {
      aggregations: null
    }
  },
  methods: {
    async getAggregations() {
      const aggregations = await getSubmissionAggregations(this.submission)
      this.aggregations = aggregations.data
      this.$refs.aggregationModal.show()
    }
  }
}
</script>
<style>
  .square-right {
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
  }
  #aggregationModal.modal.show .modal-dialog {
    margin-top: 5rem;
  }
</style>

