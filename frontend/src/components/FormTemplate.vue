<template>
  <div v-if="tab_info">
    <div class="form-sections">
      <table class="table submission-table">
        <thead>
          <tr class="first-header">
            <th v-for="(header, header_index) in tab_info.section_headers" :colspan="header.colspan" :key="header_index">
              <div v-if="header.tooltip" v-b-tooltip.hover placement="left" :title="header.tooltip">
                <span v-html="header.label"></span>  <i class="fa fa-info-circle fa-lg"></i>
              </div>
              <div v-else>
                 <span v-html="header.label"></span>
              </div>
            </th>
          </tr>
          <tr class="subheader">
            <th :colspan="subheader.colspan" v-for="(subheader, subheader_index) in tab_info.section_subheaders" :key="subheader_index">
            <div style="cursor:pointer" v-if="subheader.sort" @click="sortTable(subheader.name, tab_info.form_fields, subheader, subheader.type)">
              <span v-html="subheader.label"></span> <i v-if="subheader.sort" :class="setSortDirection(subheader.sort)"></i>
            </div>
            <div v-else>
              <span v-html="subheader.label"></span>
            </div>
            </th>
          </tr>
        </thead>

       <tbody
         @mouseover="hovered = tab_info.form_fields.indexOf(row)"
         @mouseleave="hovered = false"
          v-if="row.substance.selected"
          v-for="(row, row_index) in tab_info.form_fields"
          :key="row_index"
          class="form-fields">
          <tr v-if="tabName ==='has_produced' && row.group.selected === 'FII'" class="subheader">
            <th v-for="(subheader, subheader_index) in tab_info.special_headers.section_subheaders" :key="subheader_index">
              <small><b><div style="text-align: center" v-html="subheader.label"></div></b></small>
            </th>
          </tr>

         <tr v-if="tabName ==='has_produced' && row.group.selected === 'FII'">
           <td
           :rowspan="(['substance','blend'].includes(order) && doCommentsRow(row)) ? 2 : false"
            v-if="order != 'blend'"
            v-for="(order, order_index) in tab_info.special_fields_order"
            :key="order_index">
              <span v-b-tooltip.hover = "row[order].tooltip ? true : false" :title="row[order].tooltip" v-if="row[order].type === 'nonInput' && order != 'validation'">
                {{row[order].selected}}
              <div style="margin-left: -4rem; margin-top: 2rem" class="special-field" v-if="row.group.selected === 'EI' && (row.quantity_quarantine_pre_shipment ? row.quantity_quarantine_pre_shipment.selected : false) && order === 'decision_exempted'">
                <hr>
                Quantity of new {{tab_data.display.substances[row[order].selected]}} exported to be used for QPS applications
                <hr>
                <span>
                  <input class="form-control" type="number" v-model="row.quantity_quarantine_pre_shipment.selected">
                </span>
              </div>
              </span>

              <span class="validation-wrapper" v-else-if="row[order].type === 'nonInput' && order === 'validation'">
                <i @click="openValidation" v-if="row[order].selected.length" style="color: red; cursor: pointer" class="fa fa-exclamation fa-lg"></i>
                <i v-else style="color: green;" class="fa fa-check-square-o fa-lg "></i>

              </span>

              <span v-else>
                <fieldGenerator :fieldInfo="{index:tab_info.form_fields.indexOf(row),tabName: tabName, field:order}" :disabled="transitionState" v-if="order != 'substance' && row[order].type != 'multiselect'" :field="row[order]"></fieldGenerator>
                <span v-else-if="order === 'substance'">
                  <div class="table-btn-group">
                    <b-btn variant="info" @click="createModalData(row,tab_info.form_fields.indexOf(row))">
                      Edit
                    </b-btn>
                    <b-btn variant="outline-danger" @click="remove_field(tab_info.form_fields, row)" class="table-btn">Delete</b-btn>
                  </div>
                </span>
                <clonefield :key="`${tab_info.name}_${row_index}_${order_index}_${row.substance.selected}`" v-on:removeThisField="remove_field(tab_info.form_fields, row)" v-else-if="row[order].type === 'multiselect' && !row[order].selected" :tabName="tabName" :current_field="row"></clonefield>
                <span v-else>
                   {{tab_data.display.countries[row[order].selected]}}
                </span>
              </span>
           </td>
         </tr>

         <tr v-else>
           <td
            :colspan="row[order].colspan"
            :rowspan="(['substance','blend'].includes(order) && doCommentsRow(row)) ? 2 : false"
            v-if="order != 'blend'" v-for="(order, order_index) in tab_info.fields_order"
            :key="order_index">
              <span v-b-tooltip.hover = "row[order].tooltip ? true : false" :title="row[order].tooltip" v-if="row[order].type === 'nonInput' && order != 'validation'">
                {{row[order].selected}}
              <div style="margin-left: -4rem; margin-top: 2rem" class="special-field" v-if="row.group.selected === 'EI' && (row.quantity_quarantine_pre_shipment ? row.quantity_quarantine_pre_shipment.selected : false) && order === 'decision_exempted'">
                <hr>
                Quantity of new {{tab_data.display.substances[row.substance.selected]}} exported to be used for QPS applications
                <hr>
                <span>
                   <fieldGenerator :fieldInfo="{index:tab_info.form_fields.indexOf(row),tabName: tabName, field:order}" :disabled="transitionState" :field="row.quantity_quarantine_pre_shipment"></fieldGenerator>
                </span>
              </div>
              </span>

              <span class="validation-wrapper" v-else-if="row[order].type === 'nonInput' && order === 'validation'">
                <i @click="openValidation" v-if="row[order].selected.length" style="color: red; cursor: pointer" class="fa fa-exclamation fa-lg"></i>
                <i v-else style="color: green;" class="fa fa-check-square-o fa-lg "></i>
              </span>

              <span v-else>

                <fieldGenerator :fieldInfo="{index:tab_info.form_fields.indexOf(row),tabName: tabName, field:order}" :disabled="transitionState" v-if="order != 'substance' && row[order].type != 'multiselect'" :field="row[order]"></fieldGenerator>
                <span v-else-if="order === 'substance'">
                  {{tab_data.display.substances[row[order].selected]}}
                  <div class="table-btn-group">
                    <b-btn variant="info" @click="createModalData(row,tab_info.form_fields.indexOf(row))">
                      Edit
                    </b-btn>
                    <b-btn variant="outline-danger" @click="remove_field(tab_info.form_fields, row)" class="table-btn">Delete</b-btn>
                  </div>
                </span>
                <clonefield :key="`${tab_info.name}_${row_index}_${order_index}_${row.substance.selected}`" v-on:removeThisField="remove_field(tab_info.form_fields, row)" v-else-if="row[order].type === 'multiselect' && !row[order].selected" :tabName="tabName" :current_field="row"></clonefield>
                <span v-else>
                   {{tab_data.display.countries[row[order].selected]}}
                </span>

              </span>
           </td>
         </tr>

        <tr v-if="doCommentsRow(row)">
           <td class="comment-row" :colspan="tab_info.fields_order.length - 2">
              <b-row>
                <b-col v-for="field in ['remarks_os','remarks_party']" :key="field" lg="6">
                  <div>{{labels[field]}}</div>
                  <textarea class="form-control" v-model="row[field].selected"></textarea>
                </b-col>
              </b-row>
           </td>
         </tr>
       </tbody>

        <tbody @mouseover="hovered = tab_info.form_fields.indexOf(row)" @mouseleave="hovered = false" v-else class="form-fields">
         <tr>
           <td
           :colspan="row[order].colspan"
           :rowspan="(['substance','blend'].includes(order) && doCommentsRow(row)) ? 2 : false"
           v-if="order != 'substance'"
           v-for="(order, order_index) in tab_info.fields_order"
           :key="order_index">
              <span v-b-tooltip.hover = "row[order].tooltip ? true : false" :title="row[order].tooltip" v-if="row[order].type === 'nonInput' && order !== 'validation'">
                {{row[order].selected}}
              </span>

              <span class="validation-wrapper" v-else-if="row[order].type === 'nonInput' && order === 'validation'">
                <i @click="openValidation" v-if="row[order].selected.length" style="color: red;  cursor: pointer" class="fa fa-exclamation fa-lg"></i>
                <i v-else style="color: green;" class="fa fa-check-square-o fa-lg "></i>
              </span>

              <span v-else>
                <fieldGenerator :fieldInfo="{index:tab_info.form_fields.indexOf(row),tabName: tabName, field:order}" :disabled="transitionState" v-if="order != 'blend' && row[order].type != 'multiselect'" :field="row[order]"></fieldGenerator>
                <span v-else-if="order === 'blend'">
                  <span style="cursor:pointer;" v-b-tooltip.hover = "'Click to expand/collapse blend'" @click="row[order].expand = !row[order].expand">
                    {{tab_data.display.blends[row[order].selected].name}}
                    <i :class="`fa fa-caret-${expandedStatus(row[order].expand)}`"></i>
                  </span>

                  <div class="table-btn-group">
                    <b-btn variant="info" @click="createModalData(row,tab_info.form_fields.indexOf(row))">
                      Edit
                    </b-btn>
                    <b-btn variant="outline-danger" @click="remove_field(tab_info.form_fields, row)" class="table-btn">Delete</b-btn>
                  </div>
                </span>
                <clonefield :key="`${tab_info.name}_${row_index}_${order_index}_${row.blend.selected}`" v-on:removeThisField="remove_field(tab_info.form_fields, row)" v-else-if="row[order].type === 'multiselect' && !row[order].selected" :tabName="tabName" :current_field="row" :section="tab_info"></clonefield>
                <span v-else>
                  {{tab_data.display.countries[row[order].selected]}}
                </span>
              </span>
           </td>
         </tr>

        <tr v-if="doCommentsRow(row)">
           <td class="comment-row" :colspan="tab_info.fields_order.length - 1">
              <b-row>
                <b-col v-for="field in ['remarks_os','remarks_party']" :key="field" lg="6">
                  <div><b>{{labels[field]}}</b></div>
                  <textarea class="form-control" v-model="row[field].selected"></textarea>
                </b-col>
              </b-row>
           </td>
         </tr>

          <tr v-for="(substance, substance_index) in tab_data.display.blends[row.blend.selected].components" :key="substance_index" class="small" v-if="row.blend.expand">
            <td colspan="2">
              <div>
                <b-row>
                  <b-col>{{substance.component_name}}</b-col>
                  <b-col><b>{{substance.percentage * 100}}%</b></b-col>
                </b-row>
              </div>
            </td>

             <td
             v-if="!['substance','blend','validation','trade_party','destination_party', 'source_party','decision_exempted'].includes(order)"
             v-for="(order, order_index) in tab_info.fields_order"
             :key="order_index">
              <span v-b-tooltip.hover = "row[order].tooltip ? true : false" :title="row[order].tooltip" v-if="row[order].type === 'nonInput'">
                {{splitBlend(row[order].selected,substance.percentage)}}
              </span>
              <span v-else>
                {{splitBlend(row[order].selected,substance.percentage)}}
              </span>
           </td>
          </tr>

       </tbody>

      </table>
    </div>
    <div v-for="(comment, comment_index) in tab_info.comments" :key="comment_index" class="comments-input">
      <label>{{comment.label}}</label>
      <textarea class="form-control" v-model="comment.selected"></textarea>
    </div>
    <hr>
    <div class="footnotes">
      <p v-for="(footnote, footnote_index) in tab_info.footnotes" :key="footnote_index"><small>{{footnote}}</small></p>
    </div>

    <AppAside v-if="!transitionState" fixed>
      <DefaultAside :parentTabIndex.sync="sidebarTabIndex" :hovered="hovered" :tabName="tabName"> </DefaultAside>
    </AppAside>

    <b-modal size="lg" ref="edit_modal" id="edit_modal">
       <div v-if="modal_data" slot="modal-title">
          <span v-if="modal_data.field.substance.selected">
            {{tab_data.display.substances[modal_data.field.substance.selected]}}
          </span>
          <span v-else>
            {{tab_data.display.blends[modal_data.field.blend.selected].name}}
          </span>
       </div>
       <div v-if="modal_data">
         <b-row v-if="modal_data.field.substance.selected">
           <b-col>
              <h6>Change substance</h6>
           </b-col>
           <b-col>
              <multiselect class="mb-2" @input="updateFormField($event, {index:modal_data.index,tabName: tabName, field:'substance'})" trackBy="value" label="text" placeholder="Select substance" :value="modal_data.field.substance.selected" :options="tab_data.substances"></multiselect>
           </b-col>
         </b-row>
          <div v-for="(order, order_index) in this.tab_info.modal_order" :key="order_index">
            <b-row>
              <b-col>{{labels[order]}}</b-col>
              <b-col>
                  <fieldGenerator :fieldInfo="{index:modal_data.index,tabName: tabName, field:order}" :disabled="transitionState" v-if="modal_data.field[order].type != 'multiselect'" :field="modal_data.field[order]"></fieldGenerator>
                  <multiselect v-else :clear-on-select="true" :hide-selected="true" :close-on-select="true" trackBy="value" label="text" placeholder="Countries"  @input="updateFormField($event, {index:modal_data.index,tabName: tabName, field:order})" :value="modal_data.field[order].selected" :options="tab_data.countryOptions"></multiselect>
              </b-col>
            </b-row>
            <hr>
          </div>
          <div>
            <b-row class="mb-3" v-if="fieldsDecisionQuantity" v-for="(order,order_index) in fieldsDecisionQuantity" :key="order_index">
              <b-col lg="4" class="mb-2"><b> {{labels[`decision_${order}`]}}:</b></b-col>
              <b-col lg="4">
                <b-input-group class="modal-group" :prepend="labels['quantity']">
                  <fieldGenerator :fieldInfo="{index:modal_data.index,tabName: tabName, field:`quantity_${order}`}" :disabled="transitionState" :field="modal_data.field[`quantity_${order}`]"></fieldGenerator>
                </b-input-group>
              </b-col>
              <b-col lg="4">
                <b-input-group class="modal-group" :prepend="labels['decision']">
                  <fieldGenerator :fieldInfo="{index:modal_data.index,tabName: tabName, field:`decision_${order}`}" :disabled="transitionState" :field="modal_data.field[`decision_${order}`]"></fieldGenerator>
                </b-input-group>
              </b-col>
            </b-row>
            <hr>
          </div>
          <b-row class="mt-3" v-for="comment_field in ['remarks_os','remarks_party']" :key="comment_field">
             <b-col lg="3">
                <h6>{{labels[comment_field]}}</h6>
             </b-col>
             <b-col lg="9">
                <textarea class="form-control"  v-model="modal_data.field[comment_field].selected"></textarea>
             </b-col>
          </b-row>
       </div>
      </b-modal>

  </div>
</template>

<script>

import labels from '@/assets/labels'
import fieldGenerator from './fieldGenerator'
import CloneFieldExports from './exports/CloneFieldExports.vue'
import { Aside as AppAside } from '@coreui/vue'
import DefaultAside from './exports/DefaultAside'
import Multiselect from '@/mixins/modifiedMultiselect'

const norm = (n, sortType) => (isNaN(parseInt(n, 10)) ? (sortType === -1 ? -Infinity : Infinity) : -n)

export default {
	props: {
		tabName: String,
		tabId: Number,
		tabIndex: Number
	},

	created() {
		this.tab_info = this.$store.state.form.tabs[this.tabName]
		this.tab_data = this.$store.state.initialData
		this.labels = labels[this.tab_info.name]
	},

	components: {
		fieldGenerator,
		AppAside,
		DefaultAside,
		Multiselect,
		clonefield: CloneFieldExports
	},

	data() {
		return {
			tab_info: null,
			tab_data: null,
			modal_data: null,
			current_field: null,
			modal_comments: null,
			labels: null,
			hovered: null,
			sidebarTabIndex: 0
		}
	},

	computed: {
		fieldsDecisionQuantity() {
			if (this.tab_info.hidden_fields_order) {
				const fields = []

				for (const field of this.tab_info.hidden_fields_order) {
					const current = field.split('_')
					current.shift()
					this.pushUnique(fields, current.join('_'))
				}

				console.log('fields', fields)
				return fields
			}
			return false
		},
		transitionState() {
			return this.$store.getters.transitionState
		}
	},

	methods: {

		updateFormField(value, fieldInfo) {
			this.$store.commit('updateFormField', { value, fieldInfo })
		},

		openValidation() {
			const body = document.querySelector('body')
			this.sidebarTabIndex = 2
			body.classList.add('aside-menu-lg-show')
		},

		intersect(a, b) {
			const setA = new Set(a)
			const setB = new Set(b)
			const intersection = new Set([...setA].filter(x => setB.has(x)))
			return Array.from(intersection)
		},
		doCommentsRow(row) {
			const fieldsToShow = JSON.parse(JSON.stringify(this.tab_info.fields_order))
			const intersection = this.intersect(['remarks_os', 'remarks_party'], fieldsToShow)
			if (intersection.length === 0 && (row.remarks_os.selected || row.remarks_party.selected)) {
				return true
			}
			return false
		},

		pushUnique(array, item) {
			if (array.indexOf(item) === -1) {
				array.push(item)
			}
		},

		remove_field(parent, field) {
			this.$store.commit('removeField', { tab: this.tabName, index: parent.indexOf(field) })
		},

		getDecisions(field) {
			const decisions = []
			for (const item of field.fields) {
				const filtered = item.fields
					.filter(inner_field => inner_field.name.split('_')[0] === 'decision' && inner_field.selected)
					.map(field2 => field2.selected)
				decisions.push(filtered)
			}
			return decisions.filter(x => x[x.length - 1]).join(', ')
		},

		expandedStatus(status) {
			if (status) { return 'down' }
			return 'right'
		},

		getSpanType(field_type) {
			if (field_type === 'multiple_fields') {
				return 2
			}
		},

		getSubheaderSpanType(field_name) {
			if (field_name === 'substances' || field_name === 'quantity_exempted') { return 2 }
		},

		// isNumber(n) { return /^-?[\d.]+(?:e-?\d+)?$/.test(n); },

		splitBlend(value, percent) {
			percent *= 100
			if (value && value !== 0 && percent) {
				const count = (parseFloat(value) * parseFloat(percent)) / 100
				if (count === 0) {
					return ''
				}
				if (count < 0) {
					return count.toPrecision(3)
				} if (count > 999) {
					return parseInt(count)
				}
				return count.toPrecision(3)
			}
			return ''
		},

		createModalData(field, index) {
			this.modal_data = { field, index }
			this.$refs.edit_modal.show()
		},

		setSortDirection(value) {
			if (value === 1) {
				return 'fa fa-caret-down fa-lg'
			}
			return 'fa fa-caret-up fa-lg'
		},

		sortTable(value, section, subheader, type) {
			const self = this
			const sortType = subheader.sort

			const stringSortType = {
				'-1': 'z',
				1: 'a'
			}

			for (const field of section) {
				if (value === 'substances') {
					field.index = field.substance.selected.text
				} else {
					field.index = ''
					for (const inner_field of field.substance.inner_fields) {
						if (['destination_party', 'source_party', 'trade_party'].includes(value)) {
							if (inner_field.name === value) {
								field.index = inner_field.selected || stringSortType[sortType]
							}
						} else if (inner_field.name === value) {
							field.index = inner_field.selected
						}
					}
				}
			}

			const sortObj = JSON.parse(JSON.stringify(section))

			sortObj.sort((a, b) => {
				if (type === 'number') {
					return (norm(a.index, sortType) - norm(b.index, sortType)) * sortType
				}
				const x = self.removeSpecialChars(a.index).toUpperCase()
				const y = self.removeSpecialChars(b.index).toUpperCase()
				console.log(x, y)
				if (sortType === 1) {
					if (x > y) { return 1 }
					return -1
				}
				if (x < y) { return 1 }
				return -1
			})

			subheader.sort = -subheader.sort
			this.$set(this.tabName, 'form_fields', sortObj)
		},

		removeSpecialChars(str) {
			return str.replace(/[^a-zA-Z0-9]+/g, '')
		},

		countDecisions(field) {
			let count = 0
			for (const item of field.fields) {
				for (const subItem of item.fields) {
					if (subItem.name.split('_')[0] === 'quantity' && subItem.selected) {
						count += parseFloat(subItem.selected)
					}
				}
			}
			if (count === 0) {
				field.total = ''
			} else if (count < 0) {
				field.total = count.toPrecision(3)
			} else if (count > 999) {
				field.total = parseInt(count)
			} else {
				field.total = count.toPrecision(3)
			}
		},

		expandQuantity(field) {
			let toShow = ''
			for (const item of field.fields) {
				for (const subItem of item.fields) {
					if (subItem.name.split('_')[0] === 'quantity' && subItem.selected) {
						toShow += `${item.label}: ${subItem.selected}\n`
					}
				}
			}
			return toShow
		},

		expandDecisions(field) {
			let toShow = ''
			for (const item of field.fields) {
				for (const subItem of item.fields) {
					if (subItem.name.split('_')[0] === 'decision' && subItem.selected) {
						toShow += `${item.label}: ${subItem.selected}\n`
					}
				}
			}
			return toShow
		}

	},

	watch: {
		'tab_info.form_fields': {
			handler() {
				if (parseInt(this.tabId) === this.tabIndex) {
					if (this.tab_info.status !== 'edited') {
						this.$store.commit('setTabStatus', { tab: this.tabName, value: 'edited' })
					}
				}
			},
			deep: true
		}
	}
}
</script>

<style lang="css" scoped>
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

  .blend-name i {
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
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

  .comments-section {
    position: absolute;
    right: .5rem;
    z-index: 1;
  }

/*  .submission-table tr td:last-of-type > * {
    max-width: 90%;
  }*/

  .comment-row {
    border-bottom: 3px solid #c8ced3;
    opacity: 0.9
  }

  .fa-info-circle {
    margin-left: 5px;
  }

td[rowspan="2"] {
    vertical-align: middle;
    border-right: 1px solid #c8ced3;
    border-bottom: 3px solid #c8ced3;

}

.validation-wrapper {
    display: block;
    font-size: 1rem;
}

.validation-wrapper:hover .fa-exclamation{
  font-weight: bold;
  color: black!important;
}

</style>