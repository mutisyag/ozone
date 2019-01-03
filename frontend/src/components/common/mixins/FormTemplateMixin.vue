<script>
import inputFields from '@/components/art7/dataDefinitions/inputFields'
import fieldGenerator from '@/components/common/form-components/fieldGenerator'
import { Aside as AppAside } from '@coreui/vue'
import DefaultAside from '@/components/common/form-components/DefaultAside'
import Multiselect from '@/components/common/ModifiedMultiselect'
import { intersect } from '@/components/common/services/utilsService'

export default {
	props: {
		tabName: String,
		tabId: Number,
		tabIndex: Number
	},

	components: {
		fieldGenerator,
		AppAside,
		DefaultAside,
		Multiselect
	},

	data() {
		return {
			table: {
				emptyText: 'Please use the form on the right sidebar to add substances',
				tableFilters: false,
				pageOptions: [5, 25, 100],
				filters: {
					search: null,
					period_start: null,
					period_end: null,
					obligation: null,
					party: null,
					isCurrent: null
				}
			},

			tableBlends: {
				emptyText: 'Please use the form on the right sidebar to add blends',
				tableFilters: false,
				pageOptions: [5, 25, 100],
				filters: {
					search: null,
					period_start: null,
					period_end: null,
					obligation: null,
					party: null,
					isCurrent: null
				}
			},

			modal_data: null,
			labels: null,
			hovered: null,
			sidebarTabIndex: 0
		}
	},

	computed: {
		user() {
			// TODO: for readonly users: emptyText: 'There are no records to show'
			return null
		},
		getTabInputFields() {
			return intersect(inputFields, this.tab_info.fields_order)
		},

		blendSubstanceHeaders() {
			return this.tab_info.blend_substance_headers.filter(header => !['substance', 'percent'].includes(header))
		},

		tableItems() {
			const tableFields = []
			this.tab_info.form_fields.forEach(form_field => {
				const tableRow = {}
				Object.keys(form_field).forEach(key => {
					if (form_field.substance.selected) {
						tableRow[key] = this.typeOfDisplayObj[key]
							? this.$store.state.initialData.display[
								this.typeOfDisplayObj[key]
							][form_field[key].selected]
							: (tableRow[key] = form_field[key].selected)
					}
				})
				if (Object.keys(tableRow).length) {
					tableRow.originalObj = form_field
					tableRow.index = this.tab_info.form_fields.indexOf(form_field)
					tableRow._showDetails = true
					tableFields.push(tableRow)
				}
			})
			return tableFields
		},

		tableItemsBlends() {
			const tableFields = []
			this.tab_info.form_fields.forEach(form_field => {
				const tableRow = {}
				Object.keys(form_field).forEach(key => {
					if (form_field.blend.selected) {
						if (this.typeOfDisplayObj[key]) {
							if (this.typeOfDisplayObj[key] === 'blends') {
								tableRow[key] = this.tab_data.display[
									this.typeOfDisplayObj[key]
								][form_field[key].selected].name
							} else {
								tableRow[key] = this.tab_data.display[
									this.typeOfDisplayObj[key]
								][form_field[key].selected]
							}
						} else {
							tableRow[key] = form_field[key].selected
						}
					}
				})
				if (Object.keys(tableRow).length) {
					tableRow.originalObj = form_field
					tableRow._showDetails = false
					tableRow.index = this.tab_info.form_fields.indexOf(form_field)
					tableFields.push(tableRow)
				}
			})
			return tableFields
		},

		tableFields() {
			const tableHeaders = []
			const options = {}
			this.tab_info.section_subheaders.forEach((form_field) => {
				tableHeaders.push({
					key: form_field.name,
					label: form_field.label,
					...options
				})
			})
			return tableHeaders
		},

		tableFieldsBlends() {
			const tableHeaders = []
			const options = {}
			this.tab_info.section_subheaders.forEach((form_field) => {
				if (form_field.name === 'substance') {
					tableHeaders.push({ key: 'blend', label: '(2) <br> Blend', ...options })
				} else if (form_field.name === 'group') {
					tableHeaders.push({
						key: 'type',
						label: '(1) <br> Type',
						...options
					})
				} else {
					tableHeaders.push({
						key: form_field.name,
						label: form_field.label,
						...options
					})
				}
			})
			return tableHeaders
		},
		tab_info() {
			return this.$store.state.form.tabs[this.tabName]
		},
		tab_data() {
			return this.$store.state.initialData
		},

		allowedChanges() {
			return this.$store.getters.allowedChanges
		}
	},

	methods: {
		updateFormField(value, fieldInfo) {
			this.$store.commit('updateFormField', {
				value,
				fieldInfo
			})
			if (fieldInfo.field === 'substance') {
				this.$store.commit('updateFormField', {
					value: this.getGroupBySubstance(value),
					fieldInfo: { index: fieldInfo.index, tabName: fieldInfo.tabName, field: 'group' }
				})
			}
		},

		getGroupBySubstance(value) {
			return this.tab_data.substances.find(g => value === g.value).group.group_id
		},

		expandedStatus(status) {
			if (status) return 'down'
			return 'right'
		},
		rowHovered(item) {
			this.hovered = item.index
		},

		openValidation() {
			const body = document.querySelector('body')
			this.sidebarTabIndex = 2
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

			this.$refs.table.$el
				.querySelector('tbody')
				.addEventListener('mouseleave', () => {
					this.hovered = false
				})

			if (!this.$refs.tableHeader) {
				return
			}
			const topHeader = this.$refs.tableHeader.querySelector('tr')
			headers[0].parentNode.insertBefore(
				topHeader, headers[0]
			)
		},

		tableLoadedBlends() {
			if (!this.$refs.tableBlends) {
				return
			}

			const headers = this.$refs.tableBlends.$el.querySelectorAll('thead tr')
			if (headers.length > 1) {
				return // nothing to do, header row already created
			}

			this.$refs.tableBlends.$el
				.querySelector('tbody')
				.addEventListener('mouseleave', () => {
					this.hovered = false
				})

			if (!this.$refs.tableHeaderBlends) {
				return
			}
			const topHeader = this.$refs.tableHeaderBlends.querySelector('tr')
			if (topHeader.querySelector('th:first-of-type span').innerHTML) {
				topHeader.querySelector('th:first-of-type span').innerHTML = 'Blends'
			}
			headers[0].parentNode.insertBefore(topHeader, headers[0])
		},

		pushUnique(array, item) {
			if (array.indexOf(item) === -1) {
				array.push(item)
			}
		},

		remove_field(index) {
			this.$store.commit('removeField', { tab: this.tabName, index })
		},

		splitBlend(value, percent) {
			percent *= 100
			if (value && value !== 0 && percent) {
				const count = (parseFloat(value) * parseFloat(percent)) / 100
				if (count === 0) {
					return ''
				} if (count < 0) {
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
		}

	},

	watch: {
		'tab_info.form_fields': {
			handler() {
				if (parseInt(this.tabId) === this.tabIndex) {
					if (this.tab_info.status !== 'edited') {
						this.$store.commit('setTabStatus', {
							tab: this.tabName,
							value: 'edited'
						})
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
    text-align: center !important;
  }

  tr.small td {
    border-collapse: collapse;
    padding: 5px 0;
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
    border: 1px solid #444;
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
    transform: translateX(-50%);
  }
  .subheader th > div {
    position: relative;
    margin-bottom: 0.5rem;
  }

  .comments-section {
    position: absolute;
    right: 0.5rem;
    z-index: 1;
  }

  /*  .submission-table tr td:last-of-type > * {
      max-width: 90%;
    }*/

  .comment-row {
    border-bottom: 3px solid #c8ced3;
    opacity: 0.9;
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

  .validation-wrapper:hover .fa-exclamation {
    font-weight: bold;
    color: black !important;
  }
  .header-only {
    margin-bottom: 0;
    border-bottom: none;
  }
  .modal-footer-info {
    position: absolute;
    left: 1rem;
  }
</style>
