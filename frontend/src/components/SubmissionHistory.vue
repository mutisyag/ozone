<template>
	<div v-if="history">
		<b-row>
		   <b-col>
	            <b-input-group prepend="Search">
	              <b-form-input v-model="table.filters.search" placeholder="Type to Search" />
	              <b-input-group-append>
	                <b-btn variant="primary" :disabled="!table.filters.search" @click="table.filters.search = ''">Clear</b-btn>
	              </b-input-group-append>
	            </b-input-group>
	        </b-col>
		</b-row>
        <b-table show-empty
                   outlined
                   bordered
                   hover
                   head-variant="light"
                   stacked="md"
                   :items="history"
                   :fields="table.fields"
                   :current-page="table.currentPage"
                   :per-page="table.perPage"
                   :sort-by.sync="table.sortBy"
                   :sort-desc.sync="table.sortDesc"
                   :sort-direction="table.sortDirection"
                   :filter="table.filters.search"
                   @filtered="onFiltered"
                   ref="table"
          >
         </b-table>
		 <b-row>
	        <b-col md="6" class="my-1">
	          <b-pagination :total-rows="table.totalRows" :per-page="table.perPage" v-model="table.currentPage" class="my-0" />
	        </b-col>
	      </b-row>
	</div>
</template>

<script>
export default {

  name: 'SubmissionHistory',

  props: {
  	history: Array, 
  },

  methods: {
	onFiltered (filteredItems) {
	  // Trigger pagination to update the number of buttons/pages due to filtering
	  this.table.totalRows = filteredItems.length
	  this.table.currentPage = 1
	},
  },

  data () {
    return {
    	 table: {
          fields: [
            { key: 'user', label: 'User', sortable: true, sortDirection: 'desc', 'class': 'text-center' },
            { key: 'date', label: 'Date', sortable: true, 'class': 'text-center' },
            { key: 'current_state', label: 'Current State', sortable: true, sortDirection: 'desc', 'class': 'text-center'},
            { key: 'flag_provisional', label: 'Provisional', sortable: true, sortDirection: 'desc' , 'class': 'text-center'},
            { key: 'flag_valid', label: 'Valid', sortable: true, 'class': 'text-center'},
            { key: 'flag_superseded', label: 'Last modified', sortable: true, 'class': 'text-center'},
          ],
          currentPage: 1,
          perPage: 10,
          totalRows: 5,
          pageOptions: [ 5, 25, 100 ],
          sortBy: null,
          sortDesc: false,
          sortDirection: 'asc',
          filters: {
            search: null,
          },
          modalInfo: { title: '', content: '' }
        }
    }
  }
}
</script>

<style lang="css" scoped>
</style>