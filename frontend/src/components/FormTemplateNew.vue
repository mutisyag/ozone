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
        :items="tableItems"
        :fields="tableFields"
        :current-page="table.currentPage"
        :per-page="table.perPage"
        :sort-by.sync="table.sortBy"
        :sort-desc.sync="table.sortDesc"
        :sort-direction="table.sortDirection"
        :filter="table.filters.search"
        ref="table"
      >
        <template
          slot="substance"
          slot-scope="cell"
          v-if="!(tabName ==='has_produced' && cell.item.group === 'FII')"
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
          {{cell.item.substance}}
        </template>

        <template :slot="getCountrySlot" slot-scope="cell">
          <clonefield
            :key="`${cell.item.index}_${getCountrySlot}_${tabName}`"
            v-on:removeThisField="remove_field(cell.item.index, cell.item.originalObj)"
            v-if="!cell.item[getCountrySlot]"
            :tabName="tabName"
            :current_field="cell.item.originalObj"
          ></clonefield>
          <div v-else>{{cell.item[getCountrySlot]}}</div>
        </template>

        <template v-for="inputField in getTabInputFields" :slot="inputField" slot-scope="cell">
          <fieldGenerator
            :key="`${cell.item.index}_${inputField}_${tabName}`"
            :fieldInfo="{index:cell.item.index,tabName: tabName, field:inputField}"
            :disabled="transitionState"
            :field="cell.item.originalObj[inputField]"
            v-if="!(tabName ==='has_produced' && cell.item.group === 'FII')"
          ></fieldGenerator>
        </template>

        <template
          slot="validation"
          slot-scope="cell"
          v-if="!(tabName ==='has_produced' && cell.item.group === 'FII')"
        >
          <span class="validation-wrapper">
            <i
              @click="openValidation"
              v-if="cell.item.validation.length"
              style="color: red; cursor: pointer"
              class="fa fa-exclamation fa-lg"
            ></i>
            <i v-else style="color: green;" class="fa fa-check-square-o fa-lg"></i>
          </span>
        </template>

        <template
          v-for="tooltipField in getTabDecisionQuantityFields"
          :slot="tooltipField"
          slot-scope="cell"
          v-if="!(tabName ==='has_produced' && cell.item.group === 'FII')"
        >
          <span
            v-b-tooltip.hover="cell.item.originalObj[tooltipField].tooltip ? true : false"
            :title="cell.item.originalObj[tooltipField].tooltip"
            :key="tooltipField"
          >
            {{cell.item[tooltipField]}}
            <div
              style="margin-left: -4rem; margin-top: 2rem"
              class="special-field"
              v-if="cell.item.group === 'EI' && tooltipField === 'decision_exempted' && cell.item.quantity_quarantine_pre_shipment"
            >
              <hr>
              Quantity of new {{tab_data.display.substances[cell.item.substance.selected]}} exported to be used for QPS applications
              <hr>
              <span>
                <fieldGenerator
                  :key="tooltipField"
                  :fieldInfo="{index:cell.item.index,tabName: tabName, field:'quantity_quarantine_pre_shipment'}"
                  :disabled="transitionState"
                  :field="cell.item.originalObj.quantity_quarantine_pre_shipment"
                ></fieldGenerator>
              </span>
            </div>
          </span>
        </template>

        <template
          v-if="tabName ==='has_produced' && row.item.group === 'FII'"
          slot="row-details"
          slot-scope="row"
        >
            <div class="table-btn-group">
              <b-btn
                variant="info"
                @click="createModalData(row.item.originalObj, row.item.index)"
              >Edit</b-btn>
              <b-btn
                variant="outline-danger"
                @click="remove_field(row.item.index, row.item)"
                class="table-btn"
              >Delete</b-btn>
            </div>
            <table>
              <tr>
                <th
                  :colspan="subheader.colspan"
                  v-for="(subheader, subheader_index) in tab_info.special_headers.section_headers"
                  :key="subheader_index"
                >
                  <small>
                    <b>
                      <div style="text-align: center" v-html="subheader.label"></div>
                    </b>
                  </small>
                </th>
              </tr>

              <tr class="subheader">
                <th
                  v-for="(subheader, subheader_index) in tab_info.special_headers.section_subheaders"
                  :key="subheader_index"
                >
                  <small>
                    <b>
                      <div style="text-align: center" v-html="subheader.label"></div>
                    </b>
                  </small>
                </th>
              </tr>

              <tbody>
                <tr>
                  <td
                    v-for="specialField in tab_info.special_headers.section_subheaders"
                    :key="specialField.name"
                  >
                    <fieldGenerator
                      v-if="!['substance','decision_exempted','quantity_exempted','validation'].includes(specialField.name)"
                      :key="`${row.item.index}_${specialField.name}_${tabName}`"
                      :fieldInfo="{index:row.item.index,tabName: tabName, field:specialField.name}"
                      :disabled="transitionState"
                      :field="row.item.originalObj[specialField.name]"
                    ></fieldGenerator>
                    <span v-if="specialField.name === 'substances'">{{row.item.substance}}</span>
                    
                    <span
                      v-if="['quantity_exempted','decision_exempted'].includes(specialField.name)"
                      v-b-tooltip.hover="row.item.originalObj[specialField.name].tooltip ? true : false"
                      :title="row.item.originalObj[specialField.name].tooltip"
                    >{{row.item[specialField.name]}}</span>
                    
                    <span v-if="specialField.name === 'validation'" class="validation-wrapper">
                      <i
                        @click="openValidation"
                        v-if="row.item.validation.length"
                        style="color: red; cursor: pointer"
                        class="fa fa-exclamation fa-lg"
                      ></i>
                      <i v-else style="color: green;" class="fa fa-check-square-o fa-lg"></i>
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
        </template>
      </b-table>

      <b-table
        show-empty
        v-if="tabName != 'has_destroyed'"
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
        :filter="tableBlends.filters.search"
        ref="tableBlends"
      >
        <template slot="blend" slot-scope="cell">
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
          <span
            style="cursor:pointer;"
            v-b-tooltip.hover="'Click to expand/collapse blend'"
            @click.stop="cell.toggleDetails"
          >
            <i :class="`fa fa-caret-${expandedStatus(cell.item._showDetails)}`"></i>
            {{cell.item.blend}}
          </span>
        </template>

        <template :slot="getCountrySlot" slot-scope="cell">
          <clonefield
            :key="`${cell.item.index}_${getCountrySlot}_${tabName}`"
            v-on:removeThisField="remove_field(cell.item.index, cell.item.originalObj)"
            v-if="!cell.item[getCountrySlot]"
            :tabName="tabName"
            :current_field="cell.item.originalObj"
          ></clonefield>
          <div v-else>{{cell.item[getCountrySlot]}}</div>
        </template>

        <template v-for="inputField in getTabInputFields" :slot="inputField" slot-scope="cell">
          <fieldGenerator
            :key="`${cell.item.index}_${inputField}_${tabName}`"
            :fieldInfo="{index:cell.item.index,tabName: tabName, field:inputField}"
            :disabled="transitionState"
            :field="cell.item.originalObj[inputField]"
          ></fieldGenerator>
        </template>

        <template slot="validation" slot-scope="cell">
          <span class="validation-wrapper">
            <i
              @click="openValidation"
              v-if="cell.item.validation.length"
              style="color: red; cursor: pointer"
              class="fa fa-exclamation fa-lg"
            ></i>
            <i v-else style="color: green;" class="fa fa-check-square-o fa-lg"></i>
          </span>
        </template>

        <template
          v-for="tooltipField in getTabDecisionQuantityFields"
          :slot="tooltipField"
          slot-scope="cell"
        >
          <span
            v-b-tooltip.hover="cell.item.originalObj[tooltipField].tooltip ? true : false"
            :title="cell.item.originalObj[tooltipField].tooltip"
            :key="tooltipField"
          >{{cell.item[tooltipField]}}</span>
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
    <div
      v-for="(comment, comment_index) in tab_info.comments"
      :key="comment_index"
      class="comments-input"
    >
      <label>{{comment.label}}</label>
      <textarea class="form-control" v-model="comment.selected"></textarea>
    </div>
    <hr>
    <div class="footnotes">
      <p v-for="(footnote, footnote_index) in tab_info.footnotes" :key="footnote_index">
        <small>{{footnote}}</small>
      </p>
    </div>

    <AppAside v-if="!transitionState" fixed>
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
        <b-row v-if="modal_data.field.substance.selected">
          <b-col>
            <h6>Change substance</h6>
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
                :disabled="transitionState"
                v-if="modal_data.field[order].type != 'multiselect'"
                :field="modal_data.field[order]"
              ></fieldGenerator>
              <multiselect
                v-else
                :clear-on-select="true"
                :hide-selected="true"
                :close-on-select="true"
                trackBy="value"
                label="text"
                placeholder="Countries"
                @input="updateFormField($event, {index:modal_data.index,tabName: tabName, field:order})"
                :value="modal_data.field[order].selected"
                :options="tab_data.countryOptions"
              ></multiselect>
            </b-col>
          </b-row>
          <hr>
        </div>
        <div>
          <b-row
            class="mb-3"
            v-if="fieldsDecisionQuantity"
            v-for="(order,order_index) in fieldsDecisionQuantity"
            :key="order_index"
          >
            <b-col lg="4" class="mb-2">
              <b>{{labels[`decision_${order}`]}}:</b>
            </b-col>
            <b-col lg="4">
              <b-input-group class="modal-group" :prepend="labels['quantity']">
                <fieldGenerator
                  :fieldInfo="{index:modal_data.index,tabName: tabName, field:`quantity_${order}`}"
                  :disabled="transitionState"
                  :field="modal_data.field[`quantity_${order}`]"
                ></fieldGenerator>
              </b-input-group>
            </b-col>
            <b-col lg="4">
              <b-input-group class="modal-group" :prepend="labels['decision']">
                <fieldGenerator
                  :fieldInfo="{index:modal_data.index,tabName: tabName, field:`decision_${order}`}"
                  :disabled="transitionState"
                  :field="modal_data.field[`decision_${order}`]"
                ></fieldGenerator>
              </b-input-group>
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
            <h6>{{labels[comment_field]}}</h6>
          </b-col>
          <b-col lg="9">
            <textarea class="form-control" v-model="modal_data.field[comment_field].selected"></textarea>
          </b-col>
        </b-row>
      </div>
    </b-modal>
  </div>
</template>

<script>

import labels from "@/assets/labels";
import inputFields from "@/assets/inputFields";
import fieldGenerator from "./fieldGenerator";
import CloneFieldExports from "./exports/CloneFieldExports.vue";
import { Aside as AppAside } from "@coreui/vue";
import DefaultAside from "./exports/DefaultAside";
import Multiselect from "@/mixins/modifiedMultiselect";

const norm = (n, sortType) =>
  isNaN(parseInt(n, 10)) ? (sortType === -1 ? -Infinity : Infinity) : -n;

export default {
  props: {
    tabName: String,
    tabId: Number,
    tabIndex: Number
  },

  components: {
    fieldGenerator: fieldGenerator,
    AppAside,
    DefaultAside,
    Multiselect,
    clonefield: CloneFieldExports
  },

  created() {
    this.labels = labels[this.tab_info.name];
  },

  data() {
    return {
      table: {
        currentPage: 1,
        perPage: 200,
        totalRows: 5,
        pageOptions: [5, 25, 100],
        sortBy: null,
        sortDesc: false,
        sortDirection: "asc",
        filters: {
          search: null,
          period_start: null,
          period_end: null,
          obligation: null,
          party: null,
          isCurrent: null
        },
        modalInfo: { title: "", content: "" }
      },

      tableBlends: {
        currentPage: 1,
        perPage: 10,
        totalRows: 200,
        pageOptions: [5, 25, 100],
        sortBy: null,
        sortDesc: false,
        sortDirection: "asc",
        filters: {
          search: null,
          period_start: null,
          period_end: null,
          obligation: null,
          party: null,
          isCurrent: null
        },
        modalInfo: { title: "", content: "" }
      },

      modal_data: null,
      current_field: null,
      modal_comments: null,
      labels: null,
      hovered: null,
      sidebarTabIndex: 0,

      typeOfDisplayObj: {
        substance: "substances",
        blend: "blends",
        trade_party: "countries",
        source_party: "countries",
        destination_party: "countries"
      }
    };
  },

  computed: {
    getCountrySlot() {
      return this.intersect(
        ["source_party", "trade_party", "destination_party"],
        this.tab_info.fields_order
      )[0];
    },

    getTabDecisionQuantityFields() {
      return this.intersect(
        ["decision_exempted", "quantity_exempted"],
        this.tab_info.fields_order
      );
    },

    getTabInputFields() {
      return this.intersect(inputFields, this.tab_info.fields_order);
    },

    blendSubstanceHeaders() {
      return this.tab_info.blend_substance_headers.filter(header => {
        return !["substance", "percent"].includes(header);
      });
    },

    tableItems() {
      let tableFields = [];
      this.tab_info.form_fields.forEach((element, index) => {
        let tableRow = {};
        Object.keys(element).forEach(key => {
          if (element.substance.selected) {
            tableRow[key] = this.typeOfDisplayObj[key]
              ? this.$store.state.initialData.display[
                  this.typeOfDisplayObj[key]
                ][element[key].selected]
              : (tableRow[key] = element[key].selected);
          }
        });
        if (Object.keys(tableRow).length) {
          tableRow.originalObj = element;
          tableRow.index = this.tab_info.form_fields.indexOf(element);
          if (tableRow.group === "FII" && this.tabName === "has_produced") {
            tableRow._showDetails = true;
          }
          tableFields.push(tableRow);
        }
      });
      this.table.totalRows = tableFields.length;
      return tableFields;
    },

    tableItemsBlends() {
      let tableFields = [];
      this.tab_info.form_fields.forEach((element, index) => {
        let tableRow = {};
        Object.keys(element).forEach(key => {
          if (element.blend.selected) {
            if (this.typeOfDisplayObj[key]) {
              if (this.typeOfDisplayObj[key] === "blends") {
                tableRow[key] = this.tab_data.display[
                  this.typeOfDisplayObj[key]
                ][element[key].selected].name;
              } else {
                tableRow[key] = this.tab_data.display[
                  this.typeOfDisplayObj[key]
                ][element[key].selected];
              }
            } else {
              tableRow[key] = element[key].selected;
            }
          }
        });
        if (Object.keys(tableRow).length) {
          tableRow.originalObj = element;
          tableRow._showDetails = false;
          tableRow.index = this.tab_info.form_fields.indexOf(element);
          tableFields.push(tableRow);
        }
      });
      this.tableBlends.totalRows = tableFields.length;
      return tableFields;
    },

    tableFields() {
      const self = this;
      let tableHeaders = [];
      const options = { sortable: true, class: "text-center" };
      this.tab_info.section_subheaders.forEach((element, index) => {
        tableHeaders.push({
          key: element.name,
          label: element.label,
          ...options
        });
      });
      return tableHeaders;
    },

    tableFieldsBlends() {
      const self = this;
      let tableHeaders = [];
      const options = {
        sortable: true,
        sortDirection: "desc",
        class: "text-center"
      };
      this.tab_info.section_subheaders.forEach((element, index) => {
        if (element.name === "substance") {
          tableHeaders.push({ key: "blend", label: element.label, ...options });
        } else {
          tableHeaders.push({
            key: element.name,
            label: element.label,
            ...options
          });
        }
      });
      return tableHeaders;
    },
    tab_info() {
      return this.$store.state.form.tabs[this.tabName];
    },
    tab_data() {
      return this.$store.state.initialData;
    },

    fieldsDecisionQuantity() {
      if (this.tab_info.hidden_fields_order) {
        let fields = [];

        for (let field of this.tab_info.hidden_fields_order) {
          let current = field.split("_");
          current.shift();
          this.pushUnique(fields, current.join("_"));
        }

        console.log("fields", fields);
        return fields;
      } else {
        return false;
      }
    },
    transitionState() {
      return this.$store.getters.transitionState;
    }
  },

  methods: {
    updateFormField(value, fieldInfo) {
      this.$store.commit("updateFormField", {
        value: value,
        fieldInfo: fieldInfo
      })
    },
    
    expandedStatus(status) {
      if (status) return "down";
      else return "right";
    },
    rowHovered(item, index, event) {
      this.hovered = item.index;
    },

    openValidation() {
      const body = document.querySelector("body");
      this.sidebarTabIndex = 2;
      body.classList.add("aside-menu-lg-show");
    },

    tableLoaded() {
      if (!this.$refs.table) {
        return;
      }

      let headers = this.$refs.table.$el.querySelectorAll("thead tr");
      if (headers.length > 1) {
        return; //nothing to do, header row already created
      }

      this.$refs.table.$el
        .querySelector("tbody")
        .addEventListener("mouseleave", e => {
          this.hovered = false;
        });

      if (!this.$refs.tableHeader) {
        return;
      }
      let topHeader = this.$refs.tableHeader.querySelector("tr");
      let isCurrentTabNOTDestruction =
        this.tabName === "has_destroyed" ? false : true;
      console.log(isCurrentTabNOTDestruction, this.tabName);
      headers[0].parentNode.insertBefore(
        topHeader.cloneNode(isCurrentTabNOTDestruction),
        headers[0]
      );
    },

    tableLoadedBlends() {
      if (!this.$refs.tableBlends) {
        return;
      }

      let headers = this.$refs.tableBlends.$el.querySelectorAll("thead tr");
      if (headers.length > 1) {
        return; //nothing to do, header row already created
      }

      this.$refs.tableBlends.$el
        .querySelector("tbody")
        .addEventListener("mouseleave", e => {
          this.hovered = false;
        });

      if (!this.$refs.tableHeader) {
        return;
      }
      let topHeader = this.$refs.tableHeader.querySelector("tr");
      topHeader.querySelector("th:first-of-type span").innerHTML = "Blends";
      headers[0].parentNode.insertBefore(topHeader, headers[0]);
    },

    intersect(a, b) {
      var setA = new Set(a);
      var setB = new Set(b);
      var intersection = new Set([...setA].filter(x => setB.has(x)));
      return Array.from(intersection);
    },

    doCommentsRow(row) {
      let fieldsToShow = JSON.parse(JSON.stringify(this.tab_info.fields_order));
      let intersection = this.intersect(
        ["remarks_os", "remarks_party"],
        fieldsToShow
      );
      if (
        intersection.length === 0 &&
        (row.remarks_os.selected || row.remarks_party.selected)
      ) {
        return true;
      } else {
        return false;
      }
    },

    pushUnique(array, item) {
      if (array.indexOf(item) === -1) {
        array.push(item);
      }
    },

    remove_field(index, field) {
      this.$store.commit("removeField", { tab: this.tabName, index: index });
    },

    splitBlend(value, percent) {
      percent = percent * 100;
      if (value && value != 0 && percent) {
        let count = (parseFloat(value) * parseFloat(percent)) / 100;
        if (count === 0) {
          return "";
        } else if (count < 0) {
          return count.toPrecision(3);
        } else if (count > 999) {
          return parseInt(count);
        } else {
          return count.toPrecision(3);
        }
      } else {
        return "";
      }
    },

    createModalData(field, index) {
      this.modal_data = { field: field, index: index };
      this.$refs.edit_modal.show();
    },

  },

  watch: {
    "tab_info.form_fields": {
      handler(before, after) {
        if (parseInt(this.tabId) === this.tabIndex)
          if (this.tab_info.status != "edited") {
            this.$store.commit("setTabStatus", {
              tab: this.tabName,
              value: "edited"
            });
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
</style>
