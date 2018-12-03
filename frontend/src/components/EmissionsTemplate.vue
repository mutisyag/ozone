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
            <i style="
              font-size: 2rem;
              position: absolute;
              cursor: pointer;
              left: 17px;
              margin-top: 1.5rem;" class="fa fa-plus-circle fa-lg" @click="addField"> </i>

          </tr>
          <tr class="subheader">
            <th v-for="(subheader, subheader_index) in tab_info.section_subheaders" :key="subheader_index">
            <div style="cursor:pointer" v-if="subheader.sort" @click="sortTable(subheader.name, tab_info.form_fields, subheader, subheader.type)">
              <span v-html="subheader.label"></span> <i v-if="subheader.sort" :class="setSortDirection(subheader.sort)"></i>
            </div>
            <div v-else>
              <span v-html="subheader.label"></span>
            </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row,row_index) in tab_info.form_fields" class="form-fields" :key="row_index">
            <td v-for="(order, order_index) in tab_info.fields_order" :key="order_index">
              <span v-b-tooltip.hover = "row[order].tooltip ? true : false" :title="row[order].tooltip" v-if="row[order].type === 'nonInput'&& order !== 'validation'">
                {{row[order].selected}}
              </span>

              <span v-else-if="row[order].type === 'nonInput' && order === 'validation'">
                <i v-if="row[order].selected.length" style="color: red;" class="fa fa-exclamation fa-lg"></i>
                <i v-else style="color: green;" class="fa fa-check-square-o fa-lg "></i>
              </span>

              <fieldGenerator :fieldInfo="{index:tab_info.form_fields.indexOf(row),tabName: tabName, field:order}" v-else :field="row[order]"></fieldGenerator>
            </td>
          <td class="row-controls visible">
            <i class="fa fa-times fa-lg" @click="remove_field(tab_info.form_fields, row)"></i>
          </td>
        </tr>

        </tbody>
      </table>
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

const norm = (n, sortType) => (isNaN(parseInt(n, 10)) ? (sortType === -1 ? -Infinity : Infinity) : -n)

export default {
	props: {
		tabName: String,
		tabId: String,
		tabIndex: Number
	},

	created() {
		console.log(this.tabName)
		this.tab_info = this.$store.state.form.tabs[this.tabName]
		this.tab_data = this.$store.state.initialData
	},

	components: {
		fieldGenerator
	},

	data() {
		return {
			tab_info: null,
			tab_data: null,
			modal_data: null,
			current_field: null,
			modal_comments: null
		}
	},

	methods: {
		remove_field(field) {
			this.$store.commit('removeField', { tab: this.tabName, index: this.tab_info.form_fields.indexOf(field) })
		},

		addField() {
			this.$store.dispatch('prefillEmissionsRow')
		},

		expandedStatus(status) {
			if (status) { return 'down' }
			return 'left'
		},

		getSubheaderSpanType(field_name) {
			if (field_name === 'substances' || field_name === 'quantity_exempted') { return 2 }
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
			this.$set(this.structure, 'form_fields', sortObj)
		},

		removeSpecialChars(str) {
			return str.replace(/[^a-zA-Z0-9]+/g, '')
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
