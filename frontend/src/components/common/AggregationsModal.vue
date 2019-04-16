<template>
  <div>
    <b-btn @click="getAggregations()" variant="outline-primary">Aggregations</b-btn>
    <b-modal size="xl" ref="aggregationModal">
      <AggregationsTable :standalone="false" :aggregations="aggregations"></AggregationsTable>
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
