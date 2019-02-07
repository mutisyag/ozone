<template>
  <div :id="`${tabName}_tab`" v-if="tab_info">
    <div class="form-sections">
	<table ref="tableHeader" class="table submission-table header-only">
	<thead>
		<tr class="first-header">
		<th
			v-for="(header, header_index) in tab_info.section_headers"
			:colspan="header.colspan"
			:key="header_index">
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
			<h4> {{tab_info.formNumber}}.1 <span v-translate>Substances</span></h4>
			<div v-show="table.tableFilters" class="table-filters">
				<b-input-group :prepend="$gettext('Search')">
					<b-form-input v-model="table.filters.search"/>
				</b-input-group>
			</div>
			<i @click="table.tableFilters = !table.tableFilters" class="fa fa-filter fa-lg"></i>
		</div>
		<hr>

		<b-table
			show-empty
			outlined
			v-if="getTabInputFields"
			bordered
			@input="tableLoaded"
			@row-hovered="rowHovered"
			hover
			head-variant="light"
			stacked="md"
			class="submission-table"
			id="substance-table"
			:items="tableItems"
			:fields="tableFields"
			:empty-text="tableEmptyText"
			:filter="table.filters.search"
			ref="table">
			<template
				slot="group"
				slot-scope="cell">
				<div class="group-cell">
					{{cell.item.group}}
				</div>
				<b-btn-group class="row-controls">
					<span
						@click="createModalData(cell.item.originalObj, cell.item.index)"
					><i class="fa fa-pencil-square-o fa-lg"></i></span>
					<span
						v-if="!$store.getters.can_edit_data"
						@click="remove_field(cell.item.index, cell.item)"
						class="table-btn"
					><i class="fa fa-trash fa-lg"></i></span>
				</b-btn-group>
			</template>
			<template
				slot="substance"
				slot-scope="cell">
				<div class="substance-blend-cell">
					{{cell.item.substance}}
				</div>
			</template>

			<template
				slot="substance"
				slot-scope="cell">
				<div class="substance-blend-cell">
					{{cell.item.substance}}
				</div>
			</template>
			<template
				slot="substance"
				slot-scope="cell">
				<div class="substance-blend-cell">
					{{cell.item.substance}}
				</div>
			</template>

			<template v-for="inputField in getTabInputFields" :slot="inputField" slot-scope="cell">
				<fieldGenerator
					:key="`${cell.item.index}_${inputField}_${tabName}`"
					:fieldInfo="{index:cell.item.index,tabName: tabName, field:inputField}"
					:disabled="false"
					:field="cell.item.originalObj[inputField]" />
			</template>

			<template slot="validation" slot-scope="cell">
				<ValidationLabel :open-validation-callback="openValidation" :validation="cell.item.originalObj.validation.selected" />
			</template>
		</b-table>
	</div>
    </div>
    <hr>
    <AppAside fixed>
      <DefaultAside v-on:fillSearch="fillTableSearch($event)" :parentTabIndex.sync="sidebarTabIndex" :hovered="hovered" :tabName="tabName"></DefaultAside>
    </AppAside>

    <b-modal size="lg" ref="edit_modal" id="edit_modal">
      <div v-if="modal_data" slot="modal-title">
		<span v-if="modal_data.field.substance.selected" v-translate='{name: tab_data.display.substances[modal_data.field.substance.selected]}'>Edit %{name} substance</span>
        <span v-else v-translate='{name: tab_data.display.blends[modal_data.field.blend.selected].name}'>Edit %{name} blend</span>
      </div>
      <div v-if="modal_data">
		<p class="muted">
			<span v-translate>All the quantity values should be expressed in metric tonnes ( not ODP tonnes).</span>
			<br>
			<b><span v-translate>The values are saved automatically in the table, as you type.</span></b>
		</p>
        <b-row v-if="modal_data.field.substance.selected">
          <b-col>
            <span v-translate>Change substance</span>
          </b-col>
          <b-col>
            <multiselect
				class="mb-2"
				@input="updateFormField($event, {index:modal_data.index,tabName: tabName, field:'substance'})"
				trackBy="value"
				:disabled="$store.getters.can_edit_data"
				label="text"
				:placeholder="$gettext('Select substance')"
				:value="parseInt(modal_data.field.substance.selected)"
				:options="tab_data.substances" />
          </b-col>
        </b-row>
        <div class="mb-3" v-for="(order, order_index) in this.tab_info.modal_order" :key="order_index">
          <b-row>
            <b-col><span>{{labels[order]}}</span></b-col>
            <b-col>
              <fieldGenerator
                :fieldInfo="{index:modal_data.index,tabName: tabName, field:order}"
                :disabled="$store.getters.can_edit_data"
                v-if="modal_data.field[order].type != 'multiselect'"
                :field="modal_data.field[order]" />
              <multiselect
                v-else
                :clear-on-select="true"
                :hide-selected="true"
                :close-on-select="true"
				:disabled="$store.getters.can_edit_data"
                trackBy="value"
                label="text"
                :placeholder="$gettext('Countries')"
                @input="updateFormField($event, {index:modal_data.index,tabName: tabName, field:order})"
                :value="parseInt(modal_data.field[order].selected)"
                :options="tab_data.countryOptions" />
            </b-col>
          </b-row>
        </div>
        <b-row
          class="mt-3"
          v-for="comment_field in ['remarks_party','remarks_os']"
          :key="comment_field">
          <b-col lg="3">
            <span>{{labels[comment_field]}}</span>
          </b-col>
          <b-col lg="9">
            <textarea :disabled="getCommentFieldPermission(comment_field)"
					class="form-control" v-model="modal_data.field[comment_field].selected">
			</textarea>
          </b-col>
        </b-row>
      </div>
      <div slot="modal-footer">
          <b-btn @click="$refs.edit_modal.hide()" variant="success"><span v-translate>Close</span></b-btn>
      </div>
    </b-modal>
  </div>
</template>

<script>
import { getLabels } from '@/components/art7/dataDefinitions/labels'
import FormTemplateMixin from '@/components/common/mixins/FormTemplateMixin'
import ValidationLabel from '@/components/common/form-components/ValidationLabel'

export default {
	mixins: [FormTemplateMixin],
	components: {
		ValidationLabel
	},
	data() {
		return {
		}
	},

	props: {
		hasDisabledFields: Boolean
	},

	created() {
		this.setLabels()
	},
	methods: {
		setLabels() {
			const labels = getLabels(this.$gettext)
			this.labels = {
				...labels.common,
				...labels[this.tab_info.name]
			}
		},
		fillTableSearch(data) {
			if (data.substance) {
				this.table.filters.search = data.substance
				this.table.tableFilters = true
			}
		}
	},
	computed: {
		getTabInputFields() {
			return this.tab_info.input_fields
		},
		tableItems() {
			const tableFields = []
			this.tab_info.form_fields.forEach((element) => {
				const tableRow = {}
				Object.keys(element).forEach(key => {
					if (element.substance.selected) {
						tableRow[key] = this.typeOfDisplayObj[key]
							? this.$store.state.initialData.display[
								this.typeOfDisplayObj[key]
							][element[key].selected]
							: (tableRow[key] = element[key].selected)
					}
				})
				if (Object.keys(tableRow).length) {
					tableRow.originalObj = element
					tableRow.index = this.tab_info.form_fields.indexOf(element)
					if (tableRow.originalObj.validation.selected.length) {
						tableRow.validation = 'invalid'
					} else {
						tableRow.validation = 'valid'
					}
					tableFields.push(tableRow)
				}
			})
			return tableFields
		}
	},
	watch: {
		'$language.current': {
			handler() {
				this.setLabels()
			}
		}
	}
}
</script>
