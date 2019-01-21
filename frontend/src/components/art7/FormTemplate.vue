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

	<table v-if="hasBlends" ref="tableHeaderBlends" class="table submission-table header-only">
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

	<table v-if="tabName === 'has_produced'" ref="tableHeaderFII" class="table submission-table header-only">
	<thead>
		<tr class="first-header">
		<th
			v-for="(header, header_index) in tab_info.special_headers.section_headers"
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
			v-if="getTabInputFields && getTabDecisionQuantityFields"
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
				{{cell.item.substance}}
			</template>

			<template :slot="getCountrySlot" slot-scope="cell">
				<CloneField
					:key="`${cell.item.index}_${getCountrySlot}_${tabName}`"
					:disabled="$store.getters.can_edit_data"
					v-on:removeThisField="remove_field(cell.item.index, cell.item.originalObj)"
					v-if="!cell.item[getCountrySlot]"
					:tabName="tabName"
					:current_field="cell.item.originalObj" />
				<div v-else>{{cell.item[getCountrySlot]}}</div>
			</template>

			<template v-for="inputField in getTabInputFields" :slot="inputField" slot-scope="cell">
				<fieldGenerator
					:key="`${cell.item.index}_${inputField}_${tabName}`"
					:fieldInfo="{index:cell.item.index,tabName: tabName, field:inputField}"
					:disabled="['remarks_os', 'remarks_party'].includes(inputField) ? getCommentFieldPermission(inputField) : $store.getters.can_edit_data"
					:field="cell.item.originalObj[inputField]" />
			</template>

			<template slot="validation" slot-scope="cell">
				<ValidationLabel :open-validation-callback="openValidation" :validation="cell.item.originalObj.validation.selected" />
			</template>

			<template
				v-for="tooltipField in getTabDecisionQuantityFields"
				:slot="tooltipField"
				slot-scope="cell">
				<span
					class="edit-trigger"
					v-b-tooltip.hover="cell.item.originalObj[tooltipField].tooltip ? true : false"
					:title="cell.item.originalObj[tooltipField].tooltip"
					:key="tooltipField"
					@click="createModalData(cell.item.originalObj, cell.item.index)"
					v-if="cell.item[tooltipField]">
					{{formatQuantity(cell.item[tooltipField])}}
					<i class="fa fa-info-circle fa-lg"></i>
				</span>
				<div
					style="position: relative;z-index: 1;margin-right: -4rem; margin-top: 2rem"
					class="special-field"
					v-if="isQps.includes(parseInt(cell.item.originalObj.substance.selected)) && tooltipField === 'quantity_exempted' && cell.item.quantity_quarantine_pre_shipment"
					:key="`${tooltipField}_qps`">
					<hr>
						<span v-translate='{qps_word: qps_word, substance: tab_data.display.substances[cell.item.originalObj.substance.selected]}'>
							Quantity of new %{substance} %{qps_word} to be used for QPS applications
						</span>
					<hr>
					<span>
						<fieldGenerator
							:fieldInfo="{index:cell.item.index,tabName: tabName, field:'quantity_quarantine_pre_shipment'}"
							:disabled="$store.getters.can_edit_data"
							:field="cell.item.originalObj.quantity_quarantine_pre_shipment" />
					</span>
				</div>

				<div
					style="position: relative;z-index: 1;margin-right: -4rem; margin-top: 2rem"
					class="special-field"
					v-if="isPolyols.includes(parseInt(cell.item.originalObj.substance.selected)) && tooltipField === 'quantity_exempted' && cell.item.quantity_polyols"
					:key="`${tooltipField}_polyols`">
					<hr>
						<span v-translate>Polyols quantity</span>
					<hr>
					<span>
						<fieldGenerator
							:fieldInfo="{index:cell.item.index,tabName: tabName, field:'quantity_polyols'}"
							:disabled="$store.getters.can_edit_data"
							:field="cell.item.originalObj.quantity_polyols"	/>
					</span>
				</div>
			</template>
		</b-table>
	</div>
	<div
		v-if="tabName === 'has_produced'"
		class="table-wrapper">
		<div class="table-title">
			<h4> {{tab_info.formNumber}}.1.1 <span v-translate>Substances - group FII</span></h4>
			<div v-show="tableFII.tableFilters" class="table-filters">
				<b-input-group :prepend="$gettext('Search')">
					<b-form-input v-model="tableFII.filters.search"/>
				</b-input-group>
			</div>
			<i @click="tableFII.tableFilters = !tableFII.tableFilters" class="fa fa-filter fa-lg"></i>
		</div>
		<hr>

		<b-table
			show-empty
			outlined
			bordered
			@input="tableLoadedFII"
			@row-hovered="rowHovered"
			hover
			head-variant="light"
			stacked="md"
			class="submission-table"
			:items="tableItemsFII"
			:fields="tableFieldsFII"
			:empty-text="tableFIIEmptyText"
			:filter="tableFII.filters.search"
			ref="tableFII">
			<template
				slot="group"
				slot-scope="cell">
				<div class="group-cell">
					{{cell.item.group}}
				</div>
				<b-btn-group class="row-controls">
					<span
						variant="link"
						@click="createModalData(cell.item.originalObj, cell.item.index)">
						<i class="fa fa-pencil-square-o fa-lg"></i>
					</span>
					<span
						v-if="!$store.getters.can_edit_data"
						variant="link"
						@click="remove_field(cell.item.index, cell.item)"
						class="table-btn">
						<i class="fa fa-trash fa-lg"></i>
					</span>
				</b-btn-group>
			</template>

			<template
				slot="substance"
				slot-scope="cell">
				{{cell.item.substance}}
			</template>

			<template v-for="inputField in getTabSpecialInputFields" :slot="inputField" slot-scope="cell">
				<fieldGenerator
					:key="`${cell.item.index}_${inputField}_${tabName}`"
					:fieldInfo="{index:cell.item.index,tabName: tabName, field:inputField}"
					:disabled="$store.getters.can_edit_data"
					:field="cell.item.originalObj[inputField]" />
			</template>

			<template slot="validation" slot-scope="cell">
				<ValidationLabel :open-validation-callback="openValidation" :validation="cell.item.originalObj.validation.selected" />
			</template>

			<template
				v-for="tooltipField in getTabDecisionQuantityFields"
				:slot="tooltipField"
				slot-scope="cell">
				<span
					class="edit-trigger"
					v-b-tooltip.hover="cell.item.originalObj[tooltipField].tooltip ? true : false"
					:title="cell.item.originalObj[tooltipField].tooltip"
					:key="tooltipField"
					@click="createModalData(cell.item.originalObj, cell.item.index)"
					v-if="cell.item[tooltipField]">
					{{formatQuantity(cell.item[tooltipField])}}
					<i class="fa fa-info-circle fa-lg"></i>
				</span>
				<div
						style="position: relative;z-index: 1;margin-right: -4rem; margin-top: 2rem"
						class="special-field"
						v-if="isQps.includes(parseInt(cell.item.substance.selected)) && tooltipField === 'quantity_exempted' && cell.item.quantity_quarantine_pre_shipment"
						:key="`${tooltipField}_qps`">
						<hr>
							<span v-translate='{qps_word: qps_word, substance: tab_data.display.substances[cell.item.substance.selected]}'>
								Quantity of new %{substance} %{qps_word} to be used for QPS applications
							</span>
						<hr>
						<span>
							<fieldGenerator
								:fieldInfo="{index:cell.item.index,tabName: tabName, field:'quantity_quarantine_pre_shipment'}"
								:disabled="$store.getters.can_edit_data"
								:field="cell.item.originalObj.quantity_quarantine_pre_shipment" />
						</span>
					</div>
					<div
						style="position: relative;z-index: 1;margin-right: -4rem; margin-top: 2rem"
						class="special-field"
						v-if="isPolyols.includes(parseInt(cell.item.substance.selected)) && tooltipField === 'quantity_exempted' && cell.item.quantity_polyols"
						:key="`${tooltipField}_polyol`">
						<hr>
							<span v-translate>Quantity of Polyols</span>
						<hr>
						<span>
							<fieldGenerator
								:fieldInfo="{index:cell.item.index,tabName: tabName, field:'quantity_polyols'}"
								:disabled="$store.getters.can_edit_data"
								:field="cell.item.originalObj.quantity_polyols" />
						</span>
					</div>
			</template>
		</b-table>
	</div>
	<div
		v-if="hasBlends"
		class="table-wrapper">

		<div class="table-title">
			<h4 id="blends-table-title"> {{tab_info.formNumber}}.2 <span v-translate>Blends</span></h4>
			<div v-show="tableBlends.tableFilters" class="table-filters">
				<b-input-group :prepend="$gettext('Search')">
					<b-form-input v-model="tableBlends.filters.search"/>
				</b-input-group>
			</div>
			<i @click="tableBlends.tableFilters = !tableBlends.tableFilters" class="fa fa-filter fa-lg"></i>
		</div>
		<hr>

		<b-table
			show-empty
			v-if="hasBlends"
			outlined
			bordered
			hover
			head-variant="light"
			class="submission-table"
			@input="tableLoadedBlends"
			@row-hovered="rowHovered"
			stacked="md"
			id="blend-table"
			:items="tableItemsBlends"
			:fields="tableFieldsBlends"
			:empty-text="tableBlendsEmptyText"
			:filter="tableBlends.filters.search"
			ref="tableBlends">
			<template slot="blend" slot-scope="cell">
				<span
					style="cursor:pointer;"
					v-b-tooltip.hover="'Click to expand/collapse blend'"
					@click.stop="cell.toggleDetails">
					<i :class="`fa fa-caret-${expandedStatus(cell.item._showDetails)}`"></i>
					{{cell.item.blend}}
				</span>
			</template>
			<template slot="type" slot-scope="cell">
				<div class="group-cell">
					{{tab_data.blends.find(blend => cell.item.originalObj.blend.selected === blend.id).type}}
				</div>
				<b-btn-group class="row-controls">
					<span
						@click="createModalData(cell.item.originalObj, cell.item.index)">
						<i class="fa fa-pencil-square-o fa-lg"></i>
					</span>
					<span
						v-if="!$store.getters.can_edit_data"
						@click="remove_field(cell.item.index, cell.item)"
						class="table-btn">
						<i class="fa fa-trash fa-lg"></i>
					</span>
				</b-btn-group>
			</template>
			<template :slot="getCountrySlot" slot-scope="cell">
				<CloneField
					:disabled="$store.getters.can_edit_data"
					:key="`${cell.item.index}_${getCountrySlot}_${tabName}`"
					v-on:removeThisField="remove_field(cell.item.index, cell.item.originalObj)"
					v-if="!cell.item[getCountrySlot]"
					:tabName="tabName"
					:current_field="cell.item.originalObj" />
				<div v-else>{{cell.item[getCountrySlot]}}</div>
			</template>

			<template v-for="inputField in getTabInputFields" :slot="inputField" slot-scope="cell">
				<fieldGenerator
					:key="`${cell.item.index}_${inputField}_${tabName}`"
					:fieldInfo="{index:cell.item.index,tabName: tabName, field:inputField}"
					:disabled="['remarks_os', 'remarks_party'].includes(inputField) ? getCommentFieldPermission(inputField) : $store.getters.can_edit_data"
					:field="cell.item.originalObj[inputField]" />
			</template>

			<template slot="validation" slot-scope="cell">
				<ValidationLabel :open-validation-callback="openValidation" :validation="cell.item.originalObj.validation.selected" />
			</template>

			<template
				v-for="tooltipField in getTabDecisionQuantityFields"
				:slot="tooltipField"
				slot-scope="cell">
				<span
					class="edit-trigger"
					v-b-tooltip.hover="cell.item.originalObj[tooltipField].tooltip ? true : false"
					:title="cell.item.originalObj[tooltipField].tooltip"
					:key="tooltipField"
					@click="createModalData(cell.item.originalObj, cell.item.index)"
					v-if="cell.item[tooltipField]">
					{{formatQuantity(cell.item[tooltipField])}}
					<i class="fa fa-info-circle fa-lg"></i>
				</span>
			</template>

			<template slot="row-details" slot-scope="row">
				<thead>
					<tr>
						<th
							class="small"
							v-for="(header, header_index) in tab_info.blend_substance_headers"
							:colspan="header.colspan"
							:key="header_index">
							<span>{{labels[header]}}</span>
						</th>
					</tr>
				</thead>
				<tbody>
					<tr
						class="small"
						v-for="(substance, substance_index) in tab_data.display.blends[row.item.originalObj.blend.selected].components"
						:key="substance_index">
						<td>{{substance.component_name}}</td>
						<td>
							<b>{{(substance.percentage * 100).toPrecision(3)}}%</b>
						</td>
						<td v-for="(order, order_index) in blendSubstanceHeaders" :key="order_index">
							<!-- <span v-if="row.item[order]"> -->
							{{splitBlend(row.item[order], substance.percentage)}}
							<!-- </span> -->
						</td>
					</tr>
				</tbody>
			</template>
		</b-table>
	</div>
    </div>
    <div id="tab-comments" class="table-wrapper">
		<h4> {{tab_info.formNumber}}.{{tableCounter + 1}} <span v-translate>Comments</span></h4>
		<hr>
		<div
			v-for="(comment, comment_key) in tab_info.comments"
			:key="comment_key"
			class="comments-input">
			<label>
				<span>{{labels[comment_key]}}</span>
			</label>
				<!-- addComment(state, { data, tab, field }) { -->
			<textarea
				@change="$store.commit('addComment', {data: $event.target.value, tab:tabName, field: comment_key})"
				:disabled="getCommentFieldPermission(comment_key)"
				class="form-control"
				:value="comment.selected">
			</textarea>
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
        <div v-if="fieldsDecisionQuantity">
          <b-row
            class="mb-3"
            v-for="(order,order_index) in fieldsDecisionQuantity"
            :key="order_index"
            v-show="anotherSpecialCase(order, modal_data)">
            <b-col lg="3" class="mb-2">
              <span>{{labels[`decision_${order}`]}}</span>
            </b-col>
            <b-col lg="6">
              <b-input-group class="modal-group" :prepend="labels['quantity']">
                <fieldGenerator
					:fieldInfo="{index:modal_data.index,tabName: tabName, field:`quantity_${order}`}"
					:disabled="$store.getters.can_edit_data"
					:field="modal_data.field[`quantity_${order}`]" />
              </b-input-group>
            </b-col>
            <b-col lg="3">
              <b-input-group class="modal-group" :prepend="labels['decision']">
                <fieldGenerator
                  :fieldInfo="{index:modal_data.index,tabName: tabName, field:`decision_${order}`}"
                  :disabled="$store.getters.can_edit_data"
                  :field="modal_data.field[`decision_${order}`]" />
              </b-input-group>
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
import FormTemplateMxin from '@/components/common/mixins/FormTemplateMixin'
import { intersect } from '@/components/common/services/utilsService'
import CloneField from '@/components/common/form-components/CloneField.vue'
import ValidationLabel from '@/components/common/form-components/ValidationLabel'
import inputFields from '@/components/art7/dataDefinitions/inputFields'

export default {
	mixins: [FormTemplateMxin],
	components: {
		CloneField,
		ValidationLabel
	},
	data() {
		return {
			tableFII: {
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
			}
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
		formatQuantity(value) {
			if (!value) return
			if (typeof (value) === 'string') return value
			if (typeof (value) === 'number') {
				if (value === 0) {
					return ''
				}
				if (value < 0) {
					return value.toPrecision(3)
				}
				if (value > 999) {
					return parseInt(value)
				}
				return value.toPrecision(3)
			}
		},

		fillTableSearch(data) {
			if (data.substance && data.substance === 'HFC-23' && this.tabName === 'has_produced') {
				this.tableFII.filters.search = data.substance
				this.tableFII.tableFilters = true
			} else if (data.substance) {
				this.table.filters.search = data.substance
				this.table.tableFilters = true
			}
			if (data.blend) {
				this.tableBlends.filters.search = data.blend
				this.tableBlends.tableFilters = true
			}
		},
		anotherSpecialCase(order, modal_data) {
			// determine what are we dealing with
			const type = modal_data.field.substance && modal_data.field.substance.selected
				? 'substance'
				: modal_data.field.blend && modal_data.field.blend.selected
					? 'blend'
					: null
			// just in case
			if (!type) return
			// this may look ugly, but it had to be done
			if (!['quarantine_pre_shipment', 'polyols'].includes(order)) {
				return true
			}
			if (this.isQps.includes(parseInt(modal_data.field[type].selected)) && order === 'quarantine_pre_shipment') {
				return true
			}
			if (this.isPolyols.includes(parseInt(modal_data.field[type].selected)) && order === 'polyols') {
				return true
			}
		},

		tableLoadedFII() {
			if (!this.$refs.tableFII) {
				return
			}

			const headers = this.$refs.tableFII.$el.querySelectorAll('thead tr')
			if (headers.length > 1) {
				return // nothing to do, header row already created
			}

			this.$refs.tableFII.$el
				.querySelector('tbody')
				.addEventListener('mouseleave', () => {
					this.hovered = false
				})

			if (!this.$refs.tableHeaderFII) {
				return
			}
			const topHeader = this.$refs.tableHeaderFII.querySelector('tr')
			headers[0].parentNode.insertBefore(
				topHeader, headers[0]
			)
		}
	},
	computed: {
		qps_word() {
			let word = ''
			switch (this.tab_info.name) {
			case 'has_exports':
				word = 'exported'
				break
			case 'has_imports':
				word = 'imported'
				break
			case 'has_produced':
				word = 'produced'
				break
			case 'has_destroyed':
				word = 'destroyed'
				break
			case 'has_nonparty':
				word = 'traded'
				break
			default:
				break
			}
			return word
		},
		isPolyols() {
			return [...this.tab_data.substances.filter(s => s.is_contained_in_polyols).map(s => s.value),
				...this.tab_data.blends.filter(s => s.is_contained_in_polyols).map(s => s.id)]
		},
		isQps() {
			return [...this.tab_data.substances.filter(s => s.is_qps).map(s => s.value),
				...this.tab_data.blends.filter(s => s.is_qps).map(s => s.id)]
		},
		tableItems() {
			const tableFields = []
			this.tab_info.form_fields.forEach((element) => {
				const tableRow = {}
				Object.keys(element).forEach(key => {
					if (element.substance.selected && element.group.selected !== 'FII') {
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
		},

		tableItemsFII() {
			const tableFields = []
			this.tab_info.form_fields.forEach((element) => {
				const tableRow = {}
				Object.keys(element).forEach(key => {
					if (element.substance.selected && element.group.selected === 'FII') {
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
		},

		tableFieldsFII() {
			const tableHeaders = []
			const options = {}
			this.tab_info.special_headers.section_subheaders.forEach((element) => {
				tableHeaders.push({
					key: element.name,
					label: element.label,
					...options
				})
			})
			return tableHeaders
		},
		tableFIIEmptyText() {
			return this.$gettext('Please use the form on the right sidebar to add substances')
		},
		getTabSpecialInputFields() {
			return intersect(this.tab_info.special_fields_order, inputFields)
		},

		getCountrySlot() {
			return intersect(
				['source_party', 'trade_party', 'destination_party'],
				this.tab_info.fields_order
			)[0]
		},

		hasSubstances() {
			return Object.keys(this.$store.state.form.tabs[this.tabName].default_properties).includes('substance')
		},
		hasBlends() {
			return Object.keys(this.$store.state.form.tabs[this.tabName].default_properties).includes('blend')
		},

		tableCounter() {
			const counter = []
			if (this.hasSubstances) counter.push(1)
			if (this.hasBlends) counter.push(1)
			return counter.length
		},

		getTabDecisionQuantityFields() {
			return intersect(
				['decision_exempted', 'quantity_exempted'],
				this.tab_info.fields_order
			)
		},

		fieldsDecisionQuantity() {
			if (this.tab_info.hidden_fields_order) {
				const fields = []

				for (const field of this.tab_info.hidden_fields_order) {
					const current = field.split('_')
					current.shift()
					this.pushUnique(fields, current.join('_'))
				}

				return fields
			}
			return false
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
