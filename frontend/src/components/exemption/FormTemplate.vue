<template>
  <div :id="`${tabName}_tab`" v-if="tab_info">
    <div class="form-sections">
      <div class="table-wrapper">
        <div class="table-title">
          <h6>
            <span v-translate>Substances</span>
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
          v-if="tableRows"
          bordered
          hover
          head-variant="light"
          stacked="md"
          class="submission-table full-bordered"
          id="substance-table"
          :items="tableRows"
          :fields="tableFields"
          :empty-text="tableEmptyText"
          :filter="table.filters.search"
          ref="table"
        >
          <template v-for="field in tableFields" :slot="`HEAD_${field.key}`">
            <div v-html="field.label" :key="field.key"></div>
          </template>
          <template slot="group" slot-scope="cell">
            <div class="group-cell">{{cell.item.group}}</div>
          </template>
          <template slot="substance" slot-scope="cell">
            <div class="substance-blend-cell">{{cell.item.substance}}</div>
          </template>
          <template slot="checkForDelete" slot-scope="cell">
            <fieldGenerator
              v-show="$store.getters.can_edit_data"
              :fieldInfo="{index:cell.item.index,tabName: tabName, field:'checkForDelete'}"
              :field="cell.item.originalObj.checkForDelete"
            />
          </template>
          <template
            v-for="inputField in tab_info.rowInputFields"
            :slot="inputField"
            slot-scope="cell"
          >
            <fieldGenerator
              :key="`${cell.item.index}_${inputField}_${tabName}`"
              :fieldInfo="{index:cell.item.index,tabName: tabName, field:inputField}"
              :field="cell.item.originalObj[inputField]"
              :disabled="!$store.getters.can_edit_data"
            />
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
    <div id="tab-comments" class="table-wrapper" v-if="tab_info.comments">
      <div
        v-for="(comment, comment_key) in tab_info.comments"
        :key="comment_key"
        class="comments-input"
      >
        <label>
          <span>{{labels[comment_key]}}</span>
        </label>
        <textarea
          @change="$store.commit('addComment', {data: $event.target.value, tab:tabName, field: comment_key})"
          :disabled="getCommentFieldPermission(comment_key)"
          class="form-control"
          :value="comment.selected"
        ></textarea>
      </div>
    </div>
    <hr>
    <AppAside
      v-if="$store.getters.can_edit_data || validationLength"
      fixed
    >
      <DefaultAside
        v-on:fillSearch="fillTableSearch($event)"
        :parentTabIndex.sync="sidebarTabIndex"
        :hovered="hovered"
        :tabName="tabName"
      ></DefaultAside>
    </AppAside>

    <b-modal size="lg" ref="edit_modal" id="edit_modal" @hide="modal_data = null">
      <div v-if="modal_data" slot="modal-title">
        <span
          v-if="modal_data.field.substance.selected"
          v-translate="{name: tab_data.display.substances[modal_data.field.substance.selected]}"
        >Edit %{name} substance</span>
      </div>
      <div v-if="modal_data">
        <p class="muted">
          <span
            v-translate
          >All the quantity values should be expressed in metric tons (not ODP or CO₂-equivalent tonnes).</span>
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
        <div class="mb-3" v-for="modalField in tab_info.rowInputFields" :key="modalField">
          <b-row>
            <b-col>
              <span>{{labels[modalField]}}</span>
            </b-col>
            <b-col>
              <fieldGenerator
                :fieldInfo="{index:modal_data.index, tabName: tabName, field:modalField}"
                :disabled="!$store.getters.can_edit_data"
                :field="modal_data.field[modalField]"
              />
            </b-col>
          </b-row>
        </div>
      </div>
      <div slot="modal-footer">
        <b-btn @click="$refs.edit_modal.hide()" variant="success">
          <span v-translate>Close</span>
        </b-btn>
      </div>
    </b-modal>
  </div>
</template>

<script>
import FormTemplateMixin from '@/components/common/mixins/FormTemplateMixin'
import ValidationLabel from '@/components/common/form-components/ValidationLabel'
import { getLabels } from '@/components/exemption/dataDefinitions/labels'
import DefaultAside from '@/components/exemption/form-components/DefaultAside'

export default {
  mixins: [FormTemplateMixin],
  components: {
    ValidationLabel, DefaultAside
  },
  data() {
    return {
      tableRows: null,
      labels: null
    }
  },

  props: {
    hasDisabledFields: Boolean
  },

  created() {
    const labels = getLabels(this.$gettext)
    this.labels = {
      ...labels[this.tab_info.name]
    }
    this.setTableRows()
  },
  methods: {
    fillTableSearch(data) {
      if (data.substance) {
        this.table.filters.search = data.substance
        this.table.tableFilters = true
      }
    },
    setTableRows() {
      const tableRows = []
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
          tableRows.push(tableRow)
        }
      })
      this.tableRows = tableRows
    }
  },
  watch: {
    '$language.current': {
      handler() {
        this.setLabels()
      }
    },
    'tab_info.form_fields': {
      handler() {
        if (this.$refs.edit_modal.is_show) {
          this.tableRows = []
          setTimeout(() => this.setTableRows(), 200)
        } else {
          this.setTableRows()
        }
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
