<template>
  <div v-if="tab_info">
    <div class="form-sections">
      <div class="table-wrapper">
        <div class="table-title">
          <h4>
            {{tab_info.formNumber}}.1
            <span v-translate>Substances</span>
          </h4>
          <div v-show="table.tableFilters" class="table-filters">
            <b-input-group :prepend="$gettext('Filter')">
              <b-form-input :class="{ highlighted: table.filters.search && table.filters.search.length }" v-model="table.filters.search"/>
            </b-input-group>
          </div>
          <i @click="table.tableFilters = !table.tableFilters" class="fa fa-filter fa-lg"></i>
        </div>
        <hr>

        <b-table
          show-empty
          outlined
          bordered
          @row-clicked="rowHovered"
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
          ref="table"
        >
          <template v-for="field in tableFields" :slot="`HEAD_${field.key}`">
            <div :style="`width: ${field.width ? field.width + 'px' : 'auto'}`" v-html="field.label" :key="field.key"></div>
          </template>
          <!-- TODO: might be needed later -->
          <!-- <template slot="thead-top">
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
          </template>-->

          <template slot="group" slot-scope="cell">
            <div class="group-cell">{{cell.item.group}}</div>
            <b-btn-group class="row-controls">
              <span variant="link" @click="createModalData(cell.item.originalObj, cell.item.index)">
                 <i class="fa fa-pencil-square-o fa-lg" v-b-tooltip :title="$gettext('Edit')"></i>
              </span>
              <span
                v-if="$store.getters.can_edit_data"
                @click="remove_field(cell.item.index)"
                class="table-btn"
              >
                <i class="fa fa-trash fa-lg" v-b-tooltip :title="$gettext('Delete')"></i>
              </span>
            </b-btn-group>
          </template>
          <template slot="substance" slot-scope="cell">
            <div class="substance-blend-cell">{{cell.item.substance}}</div>
          </template>
          <template slot="quantity_import" slot-scope="cell">
            <span
              class="edit-trigger"
              v-b-tooltip.hover="cell.item.originalObj.quantity_import.tooltip ? true : false"
              :title="cell.item.originalObj.quantity_import.tooltip"
              @click="createModalData(cell.item.originalObj, cell.item.index)"
            >
              {{(cell.item.quantity_import)}}
              <i class="fa fa-info-circle fa-lg"></i>
            </span>
          </template>

          <template v-for="inputField in getTabInputFields" :slot="inputField" slot-scope="cell">
            <fieldGenerator
              :key="`${cell.item.index}_${inputField}_${tabName}`"
              :fieldInfo="{index:cell.item.index,tabName: tabName, field:inputField}"
              :disabled="['remarks_os', 'remarks_party'].includes(inputField) ? getCommentFieldPermission(inputField) : !$store.getters.can_edit_data"
              :field="cell.item.originalObj[inputField]"
            ></fieldGenerator>
          </template>
          <template slot="validation" slot-scope="cell">
            <ValidationLabel
              :open-validation-callback="openValidation"
              :validation="cell.item.originalObj.validation.selected"
            />
          </template>
        </b-table>
      </div>

      <div v-if="hasBlends" class="table-wrapper">
        <div class="table-title">
          <h4>
            {{tab_info.formNumber}}.2
            <span v-translate>Blends</span>
          </h4>
          <div v-show="tableBlends.tableFilters" class="table-filters">
            <b-input-group :prepend="$gettext('Search')">
              <b-form-input v-model="tableBlends.filters.search"/>
            </b-input-group>
          </div>
          <i
            @click="tableBlends.tableFilters = !tableBlends.tableFilters"
            class="fa fa-filter fa-lg"
          ></i>
        </div>
        <hr>
      </div>
    </div>

    <div class="table-wrapper">
      <h4>
        {{tab_info.formNumber}}.{{tableCounter + 1}}
        <span v-translate>Comments</span>
      </h4>
      <hr>
      <div
        v-for="(comment, comment_key) in tab_info.comments"
        :key="comment_key"
        class="comments-input"
      >
        <label>
          <span>{{labels[comment_key]}}</span>
        </label>
        <!-- addComment(state, { data, tab, field }) { -->
        <textarea
          @change="$store.commit('addComment', {data: $event.target.value, tab:tabName, field: comment_key})"
          :disabled="getCommentFieldPermission(comment_key)"
          class="form-control"
          :value="comment.selected"
        ></textarea>
      </div>
    </div>

    <hr>

    <div class="footnotes">
      <p v-for="(footnote, footnote_index) in tab_info.footnotes" :key="footnote_index">
        <small>{{footnote}}</small>
      </p>
    </div>
    <b-modal size="lg" ref="edit_modal" id="edit_modal" @hide="modal_data = null">
      <div v-if="modal_data" slot="modal-title">
        <span
          v-if="modal_data.field.substance.selected"
          v-translate="{name: tab_data.display.substances[modal_data.field.substance.selected]}"
        >Edit %{name} substance</span>
        <span
          v-else
          v-translate="{name: tab_data.display.blends[modal_data.field.blend.selected].name}"
        >Edit %{name} blend</span>
      </div>
      <div v-if="modal_data">
        <p class="muted">
          <span
            v-translate
          >All the quantity values should be expressed in metric tonnes ( not ODP tonnes).</span>
          <br>
          <b>
            <span v-translate>The values are saved automatically in the table, as you type.</span>
          </b>
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
              :disabled="!$store.getters.can_edit_data"
              label="text"
              :placeholder="$gettext('Select substance')"
              :value="parseInt(modal_data.field.substance.selected)"
              :options="tab_data.substances"
            />
          </b-col>
        </b-row>
        <div>Amount acquired by import & countries of manufacture</div>
        <hr>
        <b-row>
          <b-col>
            <addParties
              :parties="modal_data.field.imports"
              :index="modal_data.index"
              :tabName="tabName"
            ></addParties>
          </b-col>
        </b-row>
        <b-row
          class="mb-2 special"
          v-for="country in modal_data.field.imports"
          :key="country.party"
        >
          <b-col cols="2">{{$store.state.initialData.display.countries[country.party]}}</b-col>
          <b-col>
            <fieldGenerator
              :fieldInfo="{index:modal_data.index,tabName: tabName, field:country, party:country.party}"
              :field="country"
            />
          </b-col>
        </b-row>
        <hr>
        <div
          class="mb-3"
          v-for="(order, order_index) in tab_info.modal_order"
          :key="`modal_${order_index}`"
        >
          <b-row class="special">
            <b-col cols="3">{{labels[order]}}</b-col>
            <b-col cols="6">
              <fieldGenerator
                :fieldInfo="{index:modal_data.index,tabName: tabName, field:order}"
                :disabled="!$store.getters.can_edit_data"
                v-if="modal_data.field[order].type != 'multiselect'"
                :field="modal_data.field[order]"
              />
              <multiselect
                v-else
                :clear-on-select="true"
                :hide-selected="true"
                :close-on-select="true"
                :disabled="!$store.getters.can_edit_data"
                trackBy="value"
                label="text"
                :placeholder="$gettext('Countries')"
                @input="updateFormField($event, {index:modal_data.index,tabName: tabName, field:order})"
                :value="parseInt(modal_data.field[order].selected)"
                :options="tab_data.countryOptions"
              />
            </b-col>
          </b-row>
        </div>
        <b-row
          class="mt-3"
          v-for="comment_field in ['remarks_party','remarks_os']"
          :key="comment_field"
        >
          <b-col lg="3">
            <span>{{labels[comment_field]}}</span>
          </b-col>
          <b-col lg="9">
            <textarea
              :disabled="getCommentFieldPermission(comment_field)"
              class="form-control"
              v-model="modal_data.field[comment_field].selected"
            ></textarea>
          </b-col>
        </b-row>
      </div>
      <div slot="modal-footer">
        <b-btn @click="$refs.edit_modal.hide()" variant="success">
          <span v-translate>Close</span>
        </b-btn>
      </div>
    </b-modal>
    <AppAside fixed>
      <DefaultAside
        v-on:fillSearch="fillTableSearch($event)"
        :parentTabIndex.sync="sidebarTabIndex"
        :hovered="hovered"
        :tabName="tabName"
      ></DefaultAside>
    </AppAside>
  </div>
</template>

<script>
import ValidationLabel from '@/components/common/form-components/ValidationLabel'
import FormTemplateMxin from '@/components/common/mixins/FormTemplateMixin'
import { getLabels } from '@/components/raf/dataDefinitions/labels'
import addParties from '@/components/raf/AddParties'

export default {
  mixins: [FormTemplateMxin],
  components: {
    ValidationLabel,
    addParties
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

<style lang="scss">
  table {
    .multiselect__content-wrapper {
      min-width: 300px;
    }
  }
</style>
