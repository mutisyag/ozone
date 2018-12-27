<template>
  <div v-if="tab_info">
    <div class="form-sections">
      <table ref="tableHeader" class="table submission-table header-only">
        <thead>
          <tr class="first-header">
            <th
              v-for="(header, header_index) in tab_info.section_headers"
              :colspan="header.colspan"
              :key="header_index"
            >
              <div v-if="header.tooltip" v-b-tooltip.hover placement="left" :title="header.tooltip">
                <span v-html="header.label"></span>
                <i class="fa fa-info-circle fa-lg"></i>
              </div>
              <div v-else>
                <span v-html="header.label"></span>
              </div>
            </th>
          </tr>
        </thead>
      </table>

			<div class="table-wrapper">
				<div class="table-title">
					<h4> {{tab_info.formNumber}}.1 Facilities</h4>
					<div v-show="table.tableFilters" class="table-filters">
						<b-input-group prepend="Search all columns">
								<b-form-input v-model="table.filters.search"/>
						</b-input-group>
					</div>
					<span>
						<i @click="table.tableFilters = !table.tableFilters" class="fa fa-filter fa-lg"></i>
					</span>
				</div>
				<hr>

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
					@row-hovered="rowHovered"
					:fields="tableFields"
					@input="tableLoaded"
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

					<template slot="validation" slot-scope="cell">
						<ValidationLabel :open-validation-callback="openValidation" :validation="cell.item.validation" />
					</template>
				</b-table>
			</div>

			<b-btn class="mb-2" variant="primary"  @click="addField">
				Add facility
			</b-btn>

    </div>
		<div class="table-wapper">
			<h4> {{tab_info.formNumber}}.2 Comments</h4>
			<hr>
			<div v-for="(comment,comment_index) in tab_info.comments" class="comments-input" :key="comment_index">
				<label>{{labels[comment.name]}}</label>
				<textarea class="form-control" v-model="comment.selected"></textarea>
			</div>
		</div>
    <hr>
    <AppAside v-if="hasInvalidFields" fixed>
      <DefaultAside :parentTabIndex.sync="sidebarTabIndex" :hovered="hovered" :tabName="tabName"></DefaultAside>
    </AppAside>
  </div>
</template>

<script>

import fieldGenerator from '@/components/common/form-components/fieldGenerator'
import ValidationLabel from '@/components/common/form-components/ValidationLabel'
import inputFields from '@/components/art7/dataDefinitions/inputFields'
import DefaultAside from '@/components/common/form-components/DefaultAside'
import { Aside as AppAside } from '@coreui/vue'
import labels from '@/components/art7/dataDefinitions/labels'

export default {
	props: {
		tabName: String,
		tabId: String,
		tabIndex: Number
	},

	components: {
		fieldGenerator,
		AppAside,
		DefaultAside,
		ValidationLabel
	},

	created() {
		this.labels = labels[this.tab_info.name]
	},

	data() {
		return {
			modal_data: null,
			modal_comments: null,
			hovered: null,
			sidebarTabIndex: 0,
			table: {
				currentPage: 1,
				totalRows: 5,
				tableFilters: false,
				filters: {
					search: null,
					period_start: null,
					period_end: null,
					obligation: null,
					party: null,
					isCurrent: null
				}
			}
		}
	},

	computed: {
		tableItems() {
			const tableFields = []
			this.tab_info.form_fields.forEach(form_field => {
				const tableRow = {}
				Object.keys(form_field).forEach(key => {
					tableRow[key] = form_field[key].selected
				})
				if (Object.keys(tableRow).length) {
					tableRow.originalObj = form_field
					tableRow.index = this.tab_info.form_fields.indexOf(form_field)
					tableFields.push(tableRow)
				}
			})
			this.table.totalRows = tableFields.length
			return tableFields
		},
		tableFields() {
			const tableHeaders = []
			const options = { class: 'text-center' }
			this.tab_info.section_subheaders.forEach((form_field) => {
				tableHeaders.push({
					key: form_field.name,
					label: form_field.label,
					...options
				})
			})
			return tableHeaders
		},
		tab_info() {
			return this.$store.state.form.tabs[this.tabName]
		},
		hasInvalidFields() {
			return this.tab_info.form_fields.some(field => field.validation.selected.length)
		},
		tab_data() {
			return this.$store.state.initialData
		},
		getTabInputFields() {
			return this.intersect(inputFields, this.tab_info.fields_order)
		},
		transitionState() {
			return this.$store.getters.transitionState
		}
	},

	methods: {
		remove_field(index) {
			this.$store.commit('removeField', { tab: this.tabName, index })
		},
		rowHovered(item) {
			this.hovered = item.index
		},
		openValidation() {
			const body = document.querySelector('body')
			body.classList.add('aside-menu-lg-show')
		},
		tableLoaded() {
			if (!this.$refs.table) {
				return
			}

			const headers = this.$refs.table.$el.querySelectorAll('thead tr')
			if (headers.length > 1) {
				return // nothing to do, header row already created
			}

			if (!this.$refs.tableHeader) {
				return
			}
			const topHeader = this.$refs.tableHeader.querySelector('tr')
			headers[0].parentNode.insertBefore(
				topHeader, headers[0]
			)
		},

		intersect(a, b) {
			const setA = new Set(a)
			const setB = new Set(b)
			const intersection = new Set([...setA].filter(x => setB.has(x)))
			return Array.from(intersection)
		},
		addField() {
			this.$store.dispatch('createRow', { prefillData: null, currentSectionName: this.tabName })
		}
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
