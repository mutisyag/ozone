<template>
  <div v-if="tab_info">
    <div class="form-sections">

      <b-btn variant="success" @click="addField">Add facility</b-btn>
      <b-table
        show-empty
        outlined
        v-if="getTabInputFields"
        bordered
        hover
        head-variant="light"
        stacked="md"
        class="submission-table"
        :items="tableItems"
        :fields="tableFields"
        :current-page="table.currentPage"
        :per-page="table.perPage"
        :sort-by.sync="table.sortBy"
        :sort-desc.sync="table.sortDesc"
        :sort-direction="table.sortDirection"
        :filter="table.filters.search"
        ref="table"
      >


        <template v-for="inputField in getTabInputFields" :slot="inputField" slot-scope="cell">
          <div 
            v-if="inputField === 'facility_name'"
            class="table-btn-group"
            :key="`${cell.item.index}_${inputField}_${tabName}_button`"
            >
            <b-btn
              variant="outline-danger"
              @click="remove_field(cell.item.index)"
              class="table-btn"
            >Delete</b-btn>
          </div>
          <fieldGenerator
            :key="`${cell.item.index}_${inputField}_${tabName}`"
            :fieldInfo="{index:cell.item.index,tabName: tabName, field:inputField}"
            :disabled="transitionState"
            :field="cell.item.originalObj[inputField]"
          ></fieldGenerator>
        </template>

        <template
          slot="validation"
          slot-scope="cell"
        >
          <span class="validation-wrapper">
            <i
              v-if="cell.item.validation.length"
              style="color: red; cursor: pointer"
              class="fa fa-exclamation fa-lg"
              v-b-tooltip.hover
              title="Click here to see the validation problems"
            ></i>
            <i v-else style="color: green;" class="fa fa-check-square-o fa-lg"></i>
          </span>
        </template>

      </b-table>



    </div>
    <div v-for="(comment,comment_index) in tab_info.comments" class="comments-input" :key="comment_index">
      <label>{{comment.label}}</label>
      <textarea class="form-control" v-model="comment.selected"></textarea>
    </div>
    <hr>
    <div class="footnotes">
      <p v-for="(footnote, footnote_index) in tab_info.footnotes" :key="footnote_index"><small>{{footnote}}</small></p>
    </div>

  </div>
</template>

<script>

import fieldGenerator from './fieldGenerator'
import inputFields from "@/assets/inputFields";

const norm = (n, sortType) => (isNaN(parseInt(n, 10)) ? (sortType === -1 ? -Infinity : Infinity) : -n)

export default {
	props: {
		tabName: String,
		tabId: String,
		tabIndex: Number
	},

	components: {
		fieldGenerator
  },
  
  created(){
    console.log(this.tabName)
  },

	data() {
		return {
			modal_data: null,
      modal_comments: null,
      table: {
        currentPage: 1,
        perPage: 200,
        totalRows: 5,
        pageOptions: [5, 25, 100],
        sortBy: null,
        sortDesc: false,
        sortDirection: "asc",
        filters: {
          search: null,
          period_start: null,
          period_end: null,
          obligation: null,
          party: null,
          isCurrent: null
        }
      },
		}
  },
  
  computed: {
     tableItems() {
      let tableFields = [];
      console.log(this.tab_info)
      this.tab_info.form_fields.forEach((element, index) => {
        let tableRow = {}
        Object.keys(element).forEach(key => {
          console.log(key)
          tableRow[key] = element[key].selected
        })
        if (Object.keys(tableRow).length) {
          tableRow.originalObj = element;
          tableRow.index = this.tab_info.form_fields.indexOf(element);
          tableFields.push(tableRow);
        }
      })
      console.log(tableFields)
      this.table.totalRows = tableFields.length;
      return tableFields;
    },
    tableFields() {
      const self = this;
      let tableHeaders = [];
      const options = { sortable: true, class: "text-center" };
      this.tab_info.section_headers.forEach((element, index) => {
        tableHeaders.push({
          key: element.name,
          label: element.label,
          ...options
        });
      });
      return tableHeaders;
    },
    tab_info() {
      return this.$store.state.form.tabs[this.tabName];
    },
    tab_data() {
      return this.$store.state.initialData;
    },
    getTabInputFields() {
      return this.intersect(inputFields, this.tab_info.fields_order);
    },
    transitionState() {
      return this.$store.getters.transitionState;
    }
  },

	methods: {
		remove_field(index) {
			this.$store.commit('removeField', { tab: this.tabName, index: index})
    },
    
    intersect(a, b) {
        var setA = new Set(a);
        var setB = new Set(b);
        var intersection = new Set([...setA].filter(x => setB.has(x)));
        return Array.from(intersection);
      },
		addField() {
			this.$store.dispatch('prefillEmissionsRow')
		},
	},

	watch: {
		'tab_info.form_fields': {
			handler() {
				if (parseInt(this.tabId) === this.tabIndex) {
					if (this.tab_info.status !== 'edited') {
						this.tab_info.status = 'edited'
					}
				}
			},
			deep: true
		}
	}

}
</script>

<style lang="css" scoped>
	.form-fields td:first-of-type{
		padding-left: 2rem;
	}
  .blend {
    font-weight: bold;
  }

  td {
    text-align: center!important;
  }

  tr.small td {
    border: 1px solid #444!important;
    border-collapse: collapse;
    padding:5px 0;
  }

  tr.small td .row {
    margin-left: 0;
    margin-right: 0;
  }

  tr.small td .row:not(:last-of-type) {
    border-bottom: 1px solid #444;
  }

  tr.small {
    background: white;
  }
  tr.small th {
    border:1px solid #444;
  }

  .subheader i {
    position: absolute;
    top: 100%;
    left: 50%;
    transform:translateX(-50%);
  }
  .subheader th > div {
    position: relative;
    margin-bottom: .5rem;
  }

  .fa-info-circle {
    margin-left: 5px;
  }

  .row-controls {
    margin-top: 15px;
    position: absolute;
    left: 17px;
    width: 30px;
    background: none!important;
    padding: 0;
  }

  .row-controls i {
    font-size: 1.5rem;
    cursor: pointer;
    margin-bottom: 5px;
  }

.first-header th:first-of-type {
	padding-left: 2rem;
}

</style>
