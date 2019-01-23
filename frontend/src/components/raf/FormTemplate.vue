<template>
  <div v-if="tab_info">
    <div class="form-sections">
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
					bordered
					@row-hovered="rowHovered"
					hover
					head-variant="light"
					class="submission-table"
					:items="tableItems"
					:fields="tableFields"
					:current-page="table.currentPage"
					:per-page="table.perPage"
					:sort-by.sync="table.sortBy"
					:sort-desc.sync="table.sortDesc"
					:sort-direction="table.sortDirection"
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
					slot="quantity_import"
					slot-scope="cell">
					<span
						class="edit-trigger"
						v-b-tooltip.hover="cell.item.originalObj.quantity_import.tooltip ? true : false"
						:title="cell.item.originalObj.quantity_import.tooltip"
						>
						{{(cell.item.quantity_import)}}
						<i class="fa fa-info-circle fa-lg"></i>
					</span>
				</template>

					<template v-for="inputField in getTabInputFields" :slot="inputField" slot-scope="cell">
						<fieldGenerator
							:key="`${cell.item.index}_${inputField}_${tabName}`"
							:fieldInfo="{index:cell.item.index,tabName: tabName, field:inputField}"
							:disabled="['remarks_os', 'remarks_party'].includes(inputField) ? getCommentFieldPermission(inputField) : $store.getters.can_edit_data"
							:field="cell.item.originalObj[inputField]"
						></fieldGenerator>
					</template>
					<template slot="validation" slot-scope="cell">
						<ValidationLabel :open-validation-callback="openValidation" :validation="cell.item.originalObj.validation.selected" />
					</template>
				</b-table>
			</div>

			<div v-if="hasBlends" class="table-wrapper">
				<div class="table-title">
					<h4> {{tab_info.formNumber}}.2 <span v-translate>Blends</span></h4>
					<div v-show="tableBlends.tableFilters" class="table-filters">
						<b-input-group :prepend="$gettext('Search')">
							<b-form-input v-model="tableBlends.filters.search"/>
						</b-input-group>
					</div>
					<i @click="tableBlends.tableFilters = !tableBlends.tableFilters" class="fa fa-filter fa-lg"></i>
				</div>
				<hr>
			</div>
    </div>

	<div class="table-wrapper">
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

    <div class="footnotes">
      <p v-for="(footnote, footnote_index) in tab_info.footnotes" :key="footnote_index">
        <small>{{footnote}}</small>
      </p>
    </div>

    <AppAside fixed>
      <DefaultAside v-on:fillSearch="fillTableSearch($event)"  :parentTabIndex.sync="sidebarTabIndex" :hovered="hovered" :tabName="tabName"></DefaultAside>
    </AppAside>
  </div>
</template>

<script>
import ValidationLabel from '@/components/common/form-components/ValidationLabel'
import FormTemplateMxin from '@/components/common/mixins/FormTemplateMixin'
import { getLabels } from '@/components/hat/dataDefinitions/labels'

export default {
	mixins: [FormTemplateMxin],
	components: {
		ValidationLabel
	},
	data() {
		return {
			typeOfDisplayObj: {
				substance: 'substances',
				blend: 'blends'
			}
		}
	},
	created() {
		const labels = getLabels(this.$gettext)
		this.labels = {
			...labels.common,
			...labels[this.tab_info.name]
		}
	},
	methods: {

	},
	computed: {
		getTabInputFields() {
			return this.tab_info.input_fields
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
		}
	}
}
</script>
