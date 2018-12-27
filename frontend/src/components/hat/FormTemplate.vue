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

      <table ref="tableHeaderBlends" class="table submission-table header-only">
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
					<h4> {{tab_info.formNumber}}.1 Substances</h4>
					<div v-show="table.tableFilters" class="table-filters">
						<b-input-group prepend="Search">
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
					@input="tableLoaded"
					@row-hovered="rowHovered"
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
					:empty-text="table.emptyText"
					:filter="table.filters.search"
					ref="table"
				>
					<template
						slot="group"
						slot-scope="cell"
					>
						<div class="table-btn-group">
							<b-btn
								variant="info"
								@click="createModalData(cell.item.originalObj, cell.item.index)"
							>Edit</b-btn>
							<b-btn
								variant="outline-danger"
								@click="remove_field(cell.item.index, cell.item)"
								class="table-btn"
							>Delete</b-btn>
						</div>
						{{cell.item.group}}
					</template>
					<template v-for="inputField in getTabInputFields" :slot="inputField" slot-scope="cell">
						<fieldGenerator
							:key="`${cell.item.index}_${inputField}_${tabName}`"
							:fieldInfo="{index:cell.item.index,tabName: tabName, field:inputField}"
							:disabled="allowedChanges"
							:field="cell.item.originalObj[inputField]"
						></fieldGenerator>
					</template>
					<template
						slot="validation"
						slot-scope="cell">
						<span class="validation-wrapper">
							<b-badge
								pill
								style="cursor:pointer"
								variant="danger"
								@click="openValidation"
								v-if="cell.item.validation.length"
								v-b-tooltip.hover
								title="Click here to see the validation problems"
							>invalid</b-badge>
							<b-badge v-else pill variant="success">valid</b-badge>
						</span>
					</template>
				</b-table>
			</div>

			<div class="table-wrapper">
				<div class="table-title">
					<h4> {{tab_info.formNumber}}.2 Blends</h4>
					<div v-show="tableBlends.tableFilters" class="table-filters">
							<b-input-group prepend="Search">
									<b-form-input v-model="tableBlends.filters.search"/>
							</b-input-group>
					</div>
					<i @click="tableBlends.tableFilters = !tableBlends.tableFilters" class="fa fa-filter fa-lg"></i>
				</div>
				<hr>

				<b-table
					show-empty
					outlined
					bordered
					hover
					head-variant="light"
					class="submission-table"
					@input="tableLoadedBlends"
					@row-hovered="rowHovered"
					stacked="md"
					:items="tableItemsBlends"
					:fields="tableFieldsBlends"
					:current-page="tableBlends.currentPage"
					:per-page="tableBlends.perPage"
					:sort-by.sync="tableBlends.sortBy"
					:sort-desc.sync="tableBlends.sortDesc"
					:sort-direction="tableBlends.sortDirection"
					:empty-text="table.emptyText"
					:filter="tableBlends.filters.search"
					ref="tableBlends"
				>
					<template slot="type" slot-scope="cell">
						<div class="table-btn-group">
							<b-btn
								variant="info"
								@click="createModalData(cell.item.originalObj, cell.item.index)"
							>Edit</b-btn>
							<b-btn
								variant="outline-danger"
								@click="remove_field(cell.item.index, cell.item)"
								class="table-btn"
							>Delete</b-btn>
						</div>
						<span>{{cell.item.type}}</span>
					</template>

					<template slot="blend" slot-scope="cell">
						<span
							style="cursor:pointer;"
							v-b-tooltip.hover="'Click to expand/collapse blend'"
							@click.stop="cell.toggleDetails"
						>
							<i :class="`fa fa-caret-${expandedStatus(cell.item._showDetails)}`"></i>
							{{cell.item.blend}}
						</span>
					</template>

					<template v-for="inputField in getTabInputFields" :slot="inputField" slot-scope="cell">
						<fieldGenerator
							:key="`${cell.item.index}_${inputField}_${tabName}`"
							:fieldInfo="{index:cell.item.index,tabName: tabName, field:inputField}"
							:disabled="allowedChanges"
							:field="cell.item.originalObj[inputField]"
						></fieldGenerator>
					</template>

					<template
						slot="validation"
						slot-scope="cell">
						<span class="validation-wrapper">
							<b-badge
								pill
								style="cursor:pointer"
								variant="danger"
								@click="openValidation"
								v-if="cell.item.validation.length"
								v-b-tooltip.hover
								title="Click here to see the validation problems"
							>invalid</b-badge>
							<b-badge v-else pill variant="success">valid</b-badge>
						</span>
					</template>

					<template slot="row-details" slot-scope="row">
						<thead>
							<tr>
								<th
									class="small"
									v-for="(header, header_index) in tab_info.blend_substance_headers"
									:colspan="header.colspan"
									:key="header_index"
								>{{labels[header]}}</th>
							</tr>
						</thead>
						<tbody>
							<tr
								class="small"
								v-for="(substance, substance_index) in tab_data.display.blends[row.item.originalObj.blend.selected].components"
								:key="substance_index"
							>
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

	<div class="table-wrapper">
		<h4> {{tab_info.formNumber}}.{{tableCounter + 1}} Comments</h4>
		<hr>
		<div
			v-for="(comment, comment_index) in tab_info.comments"
			:key="comment_index"
			class="comments-input"
		>
			<label>{{labels[comment.name]}}</label>
			<textarea :disabled="$store.getters.allowedChanges" class="form-control" v-model="comment.selected"></textarea>
		</div>
	</div>

    <hr>

    <div class="footnotes">
      <p v-for="(footnote, footnote_index) in tab_info.footnotes" :key="footnote_index">
        <small>{{footnote}}</small>
      </p>
    </div>

    <AppAside v-if="!allowedChanges" fixed>
      <DefaultAside :parentTabIndex.sync="sidebarTabIndex" :hovered="hovered" :tabName="tabName"></DefaultAside>
    </AppAside>

    <b-modal size="lg" ref="edit_modal" id="edit_modal">
      <div v-if="modal_data" slot="modal-title">
        <span
          v-if="modal_data.field.substance.selected"
        >{{tab_data.display.substances[modal_data.field.substance.selected]}}</span>
        <span v-else>{{tab_data.display.blends[modal_data.field.blend.selected].name}}</span>
      </div>
      <div v-if="modal_data">
				<p class="muted">
					All the quantity values should be expressed in metric tonnes ( not ODP tonnes).
					<br>
					<b>The values are saved automatically in the table, as you type.</b>
				</p>
        <b-row v-if="modal_data.field.substance.selected">
          <b-col>
            Change substance
          </b-col>
          <b-col>
            <multiselect
              class="mb-2"
              @input="updateFormField($event, {index:modal_data.index,tabName: tabName, field:'substance'})"
              trackBy="value"
              label="text"
              placeholder="Select substance"
              :value="modal_data.field.substance.selected"
              :options="tab_data.substances"
            ></multiselect>
          </b-col>
        </b-row>
        <div v-for="(order, order_index) in this.tab_info.modal_order" :key="order_index">
          <b-row>
            <b-col>{{labels[order]}}</b-col>
            <b-col>
              <fieldGenerator
                :fieldInfo="{index:modal_data.index,tabName: tabName, field:order}"
                :disabled="allowedChanges"
                :field="modal_data.field[order]"
              ></fieldGenerator>
            </b-col>
          </b-row>
          <hr>
        </div>
        <b-row
          class="mt-3"
          v-for="comment_field in ['remarks_os','remarks_party']"
          :key="comment_field"
        >
          <b-col lg="3">
            {{labels[comment_field]}}
          </b-col>
          <b-col lg="9">
            <textarea class="form-control" v-model="modal_data.field[comment_field].selected"></textarea>
          </b-col>
        </b-row>
      </div>
      <div slot="modal-footer">
          <b-btn @click="$refs.edit_modal.hide()" variant="success">Close</b-btn>
      </div>
    </b-modal>
  </div>
</template>

<script>
import FormTemplateMxin from '@/components/common/mixins/FormTemplateMixin'
import labels from '@/components/hat/dataDefinitions/labels'

export default {
	mixins: [FormTemplateMxin],
	components: {
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
		this.labels = {
			...labels.general,
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
