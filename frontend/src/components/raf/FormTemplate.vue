<template>
  <div v-if="tab_info">
    <div class="form-sections">
      <div class="table-wrapper">
        <div class="table-title">
          <h6>
            <span v-translate>Essential uses</span>
          </h6>
          <b-btn class="mr-3" variant="outline-danger" @click="bulkRemove(selectedForDelete)" v-if="selectedForDelete.length">
            <span><span v-translate>Delete</span>&nbsp;{{selectedForDelete.length}}&nbsp;<span v-translate>selected rows</span></span>
          </b-btn>
          <div v-show="table.tableFilters" class="table-filters">
            <b-input-group :prepend="$gettext('Filter')">
              <b-form-input :class="{ highlighted: table.filters.search && table.filters.search.length }" v-model="table.filters.search"/>
            </b-input-group>
          </div>
          <i @click="table.tableFilters = !table.tableFilters" class="fa fa-filter fa-lg"></i>
        </div>

        <b-table
          show-empty
          outlined
          bordered
          hover
          head-variant="light"
          class="submission-table full-bordered"
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
          <template slot="checkForDelete" slot-scope="cell">
            <fieldGenerator
              v-show="$store.getters.can_edit_data"
              :fieldInfo="{index:cell.item.index,tabName: tabName, field:'checkForDelete'}"
              :field="cell.item.originalObj.checkForDelete"
            />
          </template>
          <template slot="group" slot-scope="cell">
            <div class="group-cell">{{cell.item.group}}</div>
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
              <span class="input text-right">
                {{(cell.item.quantity_import)}}
                <i v-if="cell.item.quantity_import" class="fa fa-info-circle fa-lg"></i>
              </span>
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
            <b-btn-group class="row-controls">
              <span  @click="createModalData(cell.item.originalObj, cell.item.index)">
                <i :class="{'fa-pencil-square-o': $store.getters.can_edit_data, 'fa-eye': !$store.getters.can_edit_data}" class="fa fa-lg"  v-b-tooltip :title="$gettext('Edit')"></i>
              </span>
              <span
                v-if="$store.getters.can_edit_data"
                @click="remove_field(cell.item.index)"
                class="table-btn"
              >
                <i class="fa fa-trash fa-lg" v-b-tooltip :title="$gettext('Delete')"></i>
              </span>
              <ValidationLabel
                :open-validation-callback="openValidation"
                :validation="cell.item.originalObj.validation.selected"
                :index="cell.item.index"
              />
            </b-btn-group>
          </template>
        </b-table>
      </div>
      <div class="table-wrapper">
        <div class="table-title">
          <h6>
            <span v-translate>Critical uses</span>
          </h6>
          <div v-show="tableCritical.tableFilters" class="table-filters">
            <b-input-group :prepend="$gettext('Filter')">
              <b-form-input :class="{ highlighted: tableCritical.filters.search && tableCritical.filters.search.length }" v-model="tableCritical.filters.search"/>
            </b-input-group>
          </div>
          <i @click="tableCritical.tableFilters = !tableCritical.tableFilters" class="fa fa-filter fa-lg"></i>
        </div>

        <b-table
          show-empty
          outlined
          bordered
          hover
          head-variant="light"
          class="submission-table full-bordered"
          :items="tableItemsCritical"
          :fields="tableFieldsCritical"
          :current-page="tableCritical.currentPage"
          :per-page="tableCritical.perPage"
          :sort-by.sync="tableCritical.sortBy"
          :sort-desc.sync="tableCritical.sortDesc"
          :sort-direction="tableCritical.sortDirection"
          :empty-text="tableEmptyText"
          :filter="tableCritical.filters.search"
          ref="tableCritical"
        >
          <template v-for="field in tableFieldsCritical" :slot="`HEAD_${field.key}`">
            <div :style="`width: ${field.width ? field.width + 'px' : 'auto'}`" v-html="field.label" :key="field.key"></div>
          </template>
          <template slot="group" slot-scope="cell">
            <div class="group-cell">{{cell.item.group}}</div>
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
              <span class="input text-right">
                {{(cell.item.quantity_import)}}
                <i v-if="cell.item.quantity_import" class="fa fa-info-circle fa-lg"></i>
              </span>
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
            <b-btn-group class="row-controls">
              <span  @click="createModalData(cell.item.originalObj, cell.item.index)">
               <i :class="{'fa-pencil-square-o': $store.getters.can_edit_data, 'fa-eye': !$store.getters.can_edit_data}" class="fa fa-lg"  v-b-tooltip :title="$gettext('Edit')"></i>
              </span>
              <span
                v-if="$store.getters.can_edit_data"
                @click="remove_field(cell.item.index)"
                class="table-btn"
              >
                <i class="fa fa-trash fa-lg" v-b-tooltip :title="$gettext('Delete')"></i>
              </span>
              <ValidationLabel
                :open-validation-callback="openValidation"
                :validation="cell.item.originalObj.validation.selected"
                :index="cell.item.index"
              />
            </b-btn-group>
          </template>
        </b-table>
      </div>
    </div>

    <div class="table-wrapper">
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
        <b-row v-if="modal_data.field.substance.selected && !isCritical">
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
            <b-col cols="3">{{specialLabels(order, modal_data.field.substance.selected)}}</b-col>
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
        v-if="$store.getters.can_edit_data || validationLength"
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
import DefaultAside from '@/components/raf/form-components/DefaultAside'

export default {
  mixins: [FormTemplateMxin],
  components: {
    ValidationLabel,
    addParties,
    DefaultAside
  },
  data() {
    return {
      typeOfDisplayObj: {
        substance: 'substances',
        blend: 'blends'
      },
      tableCritical: {
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
  created() {
    const labels = getLabels(this.$gettext)
    this.labels = {
      ...labels.common,
      ...labels[this.tab_info.name]
    }
  },
  methods: {
    specialLabels(field, substance) {
      if (this.isCritical) {
        console.log('substance - ', substance)
        return this.labels.critical[field]
      }
      return this.labels[field]
    }
  },
  computed: {
    emergency_field() {
      return this.tab_info.form_fields.map((field, index) => ({ index, emergency: field.is_emergency.selected }))
    },
    isCritical() {
      return this.modal_data.field.substance.selected && this.$store.state.initialData.substances.find(s => parseInt(s.value) === parseInt(this.modal_data.field.substance.selected)).has_critical_uses
    },
    currentPeriod() {
      return this.$store.state.current_submission.reporting_period
    },
    tableItems() {
      const tableFields = []
      this.tab_info.form_fields.forEach(form_field => {
        const tableRow = {}
        Object.keys(form_field).forEach(key => {
          if (form_field.substance.selected && !this.$store.getters.getCriticalSubstances(form_field.substance.selected)) {
            tableRow[key] = this.typeOfDisplayObj[key]
              ? this.$store.state.initialData.display[
                this.typeOfDisplayObj[key]
              ][form_field[key].selected]
              : (tableRow[key] = form_field[key].selected)
            tableRow.year = this.currentPeriod
          }
        })
        if (Object.keys(tableRow).length) {
          tableRow.originalObj = form_field
          tableRow.index = this.tab_info.form_fields.indexOf(form_field)
          tableRow._showDetails = true
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

    tableItemsCritical() {
      const tableFields = []
      this.tab_info.form_fields.forEach((element) => {
        const tableRow = {}
        Object.keys(element).forEach(key => {
          if (element.substance.selected && this.$store.getters.getCriticalSubstances(element.substance.selected)) {
            tableRow[key] = this.typeOfDisplayObj[key]
              ? this.$store.state.initialData.display[
                this.typeOfDisplayObj[key]
              ][element[key].selected]
              : (tableRow[key] = element[key].selected)
            tableRow.year = this.currentPeriod
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

    tableFieldsCritical() {
      const tableHeaders = []
      const options = {}
      this.tab_info.section_subheaders_critical.forEach((form_field) => {
        const header = {
          key: form_field.name,
          label: form_field.label,
          width: form_field.width || null,
          ...options
        }
        tableHeaders.push(header)
      })
      return tableHeaders
    },

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
  },
  watch: {
    emergency_field: {
      handler(new_val, old_val) {
        if (!old_val || !old_val.length || (old_val.length !== new_val.length)) return
        Object.keys(new_val).forEach(key => {
          if (new_val[key].emergency !== old_val[key].emergency) {
            this.$store.commit('setExemptionBasedOnEmergency', { emergency: new_val[key].emergency, index: new_val[key].index })
          }
        })
      },
      deep: true
    }
  }
}
</script>

<style lang="scss">
  table {
    .multiselect__content-wrapper {
      min-width: 300px;
    }
    td {
      vertical-align: middle!important;
    }
  }
</style>
