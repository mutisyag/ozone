<template>
  <div v-if="tab_info">
    <div class="form-sections">
      <table class="table submission-table">
        <thead>
          <tr class="first-header">
            <th v-for="header in tab_info.section_headers" :colspan="header.colspan">
              <div v-if="header.tooltip" v-b-tooltip.hover placement="left" :title="header.tooltip">
                <span v-html="header.label"></span>  <i class="fa fa-info-circle fa-lg"></i>
              </div>
              <div v-else>
                 <span v-html="header.label"></span>
              </div>
            </th>
          </tr>
          <tr class="subheader">
            <th v-for="subheader in tab_info.section_subheaders">
            <div style="cursor:pointer" v-if="subheader.sort" @click="sortTable(subheader.name, tab_info.form_fields, subheader, subheader.type)">
              <span v-html="subheader.label"></span> <i v-if="subheader.sort" :class="setSortDirection(subheader.sort)"></i>
            </div>  
            <div v-else>
              <span v-html="subheader.label"></span>
            </div>
            </th>
          </tr>
        </thead>
       <tbody v-if="row.substance.selected" v-for="(row, row_index) in tab_info.form_fields" class="form-fields">
         <tr>
           <td v-if="order != 'blend'" v-for="(order, order_index) in tab_info.fields_order">

              <span v-b-tooltip.hover = "row[order].tooltip ? true : false" :title="row[order].tooltip" v-if="row[order].type === 'nonInput' && order != 'validation'">
                {{row[order].selected}}
              <div style="margin-left: -4rem; margin-top: 2rem" class="special-field" v-if="row.group.selected === 'EI' && (row.quantity_quarantine_pre_shipment ? row.quantity_quarantine_pre_shipment.selected : false) && order === 'decision_exempted'">
                <hr>
                Quantity of new {{labels['quantity_quarantine_pre_shipment']}} exported to be used for QPS applications
                <hr>
                <span>
                  <input class="form-control" type="number" v-model="row.quantity_quarantine_pre_shipment.selected">
                </span>
              </div>
              </span>

              <span v-else-if="row[order].type === 'nonInput' && order === 'validation'">
                <i v-if="row[order].selected.length" style="color: red;" class="fa fa-times-circle fa-lg mt-4"></i>
                <i v-else style="color: green;" class="fa fa-check-circle fa-lg mt-4"></i>

              </span>

              <span v-else>
                <fieldGenerator v-if="order != 'substance' && row[order].type != 'multiselect'" :field="row[order]"></fieldGenerator>
                <span v-else-if="order === 'substance'">
                  {{getRowSubstance(row[order].selected)}}
                  <div class="table-btn-group">
                    <b-btn variant="info" @click="createModalData(row)">
                      Edit
                    </b-btn>
                    <b-btn variant="outline-danger" @click="remove_field(tab_info.form_fields, row)" class="table-btn">Delete</b-btn>
                  </div>
                </span>
                <clonefield :key="`${tab_info.name}_${row_index}_${order_index}_${row.substance.selected}`" v-on:removeThisField="remove_field(tab_info.form_fields, row)" v-else-if="row[order].type === 'multiselect' && !row[order].selected" :sectionName="tab_info.name" :countryOptions="data.countryOptions" :current_field="row" :section="tab_info"></clonefield>
                <span v-else>
                  {{getRowCountry(row[order].selected)}}
                </span>
              </span>
           </td>
         </tr>
       </tbody>

        <tbody v-if="row.blend.selected" v-for="(row, row_index) in tab_info.form_fields" class="form-fields">
         <tr>
           <td v-if="order != 'substance'" v-for="(order, order_index) in tab_info.fields_order">
              <span v-b-tooltip.hover = "row[order].tooltip ? true : false" :title="row[order].tooltip" v-if="row[order].type === 'nonInput'">
                {{row[order].selected}}
              </span>
              <span v-else>
                <fieldGenerator v-if="order != 'blend' && row[order].type != 'multiselect'" :field="row[order]"></fieldGenerator>
                <span v-else-if="order === 'blend'">
                  <span style="cursor:pointer;" @click="row[order].expand = !row[order].expand">{{getRowBlend(row[order].selected)}} <i :class="`fa fa-caret-square-o-${expandedStatus(row[order].expand)}`"></i></span>

                  <div class="table-btn-group">
                    <b-btn variant="info" @click="createModalData(row)">
                      Edit
                    </b-btn>
                    <b-btn variant="outline-danger" @click="remove_field(tab_info.form_fields, row)" class="table-btn">Delete</b-btn>
                  </div>
                </span>
                <clonefield :key="`${tab_info.name}_${row_index}_${order_index}_${row.blend.selected}`" v-on:removeThisField="remove_field(tab_info.form_fields, row)" v-else-if="row[order].type === 'multiselect' && !row[order].selected" :sectionName="tab_info.name" :countryOptions="data.countryOptions" :current_field="row" :section="tab_info"></clonefield>
                <span v-else>
                  {{getRowCountry(row[order].selected)}}
                </span>
              </span>
           </td>
         </tr>


          <tr v-for="substance in getBlendSubstances(row.blend.selected).components" class="small" v-if="row.blend.expand">

            <td colspan="2">
              <div>
                <b-row>
                  <b-col>{{substance.substance_name}}</b-col>
                  <b-col><b>{{substance.percentage}}%</b></b-col>
                </b-row>
              </div>
            </td>
            
             <td v-if="!['substance','blend','validation','trade_party','destination_party', 'source_party','decision_exempted'].includes(order)" v-for="(order, order_index) in tab_info.fields_order">
              <span v-b-tooltip.hover = "row[order].tooltip ? true : false" :title="row[order].tooltip" v-if="row[order].type === 'nonInput'">
                {{splitBlend(row[order].selected,substance.percentage)}}
              </span>
              <span v-else>
                {{splitBlend(row[order].selected,substance.percentage)}}
              </span>
           </td>

     
          </tr>
       </tbody>

      </table>
    </div>
    <div v-for="comment in tab_info.comments" class="comments-input">
      <label>{{comment.label}}</label>
      <textarea class="form-control" v-model="comment.selected"></textarea>
    </div>
    <hr>
    <div class="footnotes">
      <p v-for="footnote in tab_info.footnotes"><small>{{footnote}}</small></p>
    </div>

    <AppAside fixed>
      <DefaultAside :data="tab_data" :form="tab_info"> </DefaultAside>
    </AppAside>

    <b-modal size="lg" ref="edit_modal" id="edit_modal">
       <div v-if="modal_data" slot="modal-title">
          <span v-if="modal_data.substance.selected">
            {{getRowSubstance(modal_data.substance.selected)}}
          </span>
          <span v-else>
            {{getRowBlend(modal_data.blend.selected)}}
          </span>
       </div>
       <div v-if="modal_data">
         <b-row v-if="modal_data.substance.selected">
           <b-col>
              <h6>Change substance</h6>
           </b-col>
           <b-col>
              <multiselect class="mb-2" trackBy="value" label="text" placeholder="Select substance" v-model="modal_data.substance.selected" :options="data.substances"></multiselect>
           </b-col>
         </b-row>
          <div v-for="order in this.tab_info.modal_order">
            <b-row>
              <b-col>{{labels[order]}}</b-col>
              <b-col>
                  <fieldGenerator v-if="modal_data[order].type != 'multiselect'" :field="modal_data[order]"></fieldGenerator>
                  <multiselect v-else :clear-on-select="true" :hide-selected="true" :close-on-select="true" trackBy="value" label="text" placeholder="Countries" v-model="modal_data[order].selected" :options="data.countryOptions"></multiselect>
              </b-col>
            </b-row>
            <hr>
          </div>
          <div>
            <b-row v-if="fieldsDecisionQuantity" v-for="order in fieldsDecisionQuantity">
              <b-col lg="12" class="mb-2"><b> {{labels[`decision_${order}`]}}</b></b-col>
              <b-col>
                    {{labels['quantity']}}
                    <fieldGenerator :field="modal_data[`quantity_${order}`]"></fieldGenerator>
              </b-col>
              <b-col>
                  {{labels['decision']}}
                    <fieldGenerator :field="modal_data[`decision_${order}`]"></fieldGenerator>
              </b-col>
            </b-row>
            <hr>
          </div>
          <b-row class="mt-3" v-for="comment_field in ['remarks_os','remarks_party']">
             <b-col lg="3">
                <h6>{{labels[comment_field]}}</h6>
             </b-col>
             <b-col lg="9">
                <textarea class="form-control"  v-model="modal_data[comment_field].selected"></textarea>
             </b-col>
          </b-row>
       </div>
      </b-modal>

  </div>
</template>

<script>


import labels from '@/assets/labels'
import fieldGenerator from "./fieldGenerator"
import CloneFieldExports from './exports/CloneFieldExports.vue' 
import {Aside as AppAside} from '@coreui/vue'
import DefaultAside from './exports/DefaultAside'
import Multiselect from '@/mixins/modifiedMultiselect'

export default {
  props: {
    structure: Object,
    data: Object
  },

  created(){
    this.tab_info = this.structure
    this.tab_data = this.data
    this.labels = labels[this.tab_info.name]
  },

  components: {
    fieldGenerator: fieldGenerator, 
    AppAside, DefaultAside, Multiselect, 
    clonefield: CloneFieldExports 
  },


  data () {
    return {
      tab_info: null,
      tab_data: null,
      modal_data: null,
      current_field: null,
      modal_comments: null,
      labels: null,
    }
  },

  computed: {
    fieldsDecisionQuantity(){
      if(this.tab_info.hidden_fields_order){
        let fields = []

        for(let field of this.tab_info.hidden_fields_order) {
          let current = field.split('_')
          current.shift()
          this.pushUnique(fields, current.join('_'))
        }
        return fields
      } else {
        return false
      }
    },
  },

  methods: {

    pushUnique(array, item) {
      if (array.indexOf(item) === -1) {
        array.push(item);
      }
    },
 
    remove_field(parent, field) {
      parent.splice(parent.indexOf(field), 1)
    },

    getBlendSubstances(blend_id){
      return this.data.blends.find(blend => blend.id === blend_id)
    },

    getRowSubstance(substance_id) {
      return this.data.substances.find(substance => substance.value === substance_id).text
    },
    getRowBlend(blend_id) {
      return this.data.blends.find(blend => blend.id === blend_id).blend_id
    },

    getRowCountry(country_id){
      return this.data.countryOptions.find(country => country.value === country_id).text
    },

    getDecisions(field){
      let decisions = []
      for(let item of field.fields) {
        let filtered = item.fields
                        .filter(inner_field => inner_field.name.split('_')[0] === 'decision' && inner_field.selected)
                        .map(field => field.selected) 
        decisions.push(filtered)
      }
      return decisions.filter( x => x[x.length - 1]).join(', ')
    },

    expandedStatus(status) {
      if(status) 
        return 'down'
      else 
        return 'up'
    },

    getSpanType(field_type) {
      if(field_type === 'multiple_fields'){
        return 2
      }
    }, 

    getSubheaderSpanType(field_name){
      if(field_name === 'substances' || field_name ==='quantity_exempted')
        return 2
    },

    // isNumber(n) { return /^-?[\d.]+(?:e-?\d+)?$/.test(n); },

    splitBlend(value, percent) {
      if(value && value != 0 && percent) {
        let count = (parseFloat(value) * parseFloat(percent))/100
        if(count === 0) {
          return ''
        }
        else if(count < 0) {
          return count.toPrecision(3)
        } else if(count > 999) {
          return parseInt(count)
        } else {
          return count.toPrecision(3)
        }
      } else {
        return ''
      }
    },

    createModalData(field) {
      this.modal_data = field
      this.$refs.edit_modal.show()
    },

    setSortDirection(value) {
      if(value === 1) {
        return 'fa fa-caret-down fa-lg'
      } else {
        return 'fa fa-caret-up fa-lg'
      }
    },


    sortTable(value, section, subheader, type){
      var self = this
      let sortType = subheader.sort

      let stringSortType = {
        '-1': 'z',
        '1': 'a' 
      }

      for(let field of section) {
          if(value === 'substances') {
            field.index = field.substance.selected.text
          }
          else {
            field.index = ''
            for(let inner_field of field.substance.inner_fields) {
              if(['destination_party','source_party', 'trade_party'].includes(value)) {
                if(inner_field.name === value){
                  field.index = inner_field.selected || stringSortType[sortType]
                }
              }
              else {
                if(inner_field.name === value) {
                  field.index = inner_field.selected
                }
              }
            }
          }
        }

      let sortObj = JSON.parse(JSON.stringify(section))
      function norm(n) {
        return isNaN(parseInt(n, 10)) ? (sortType === -1 ? -Infinity:Infinity) : -n;
      }
      sortObj.sort(function(a,b){
        if(type === 'number') {
          return (norm(a.index) - norm(b.index)) * sortType
        } else {
          var x = self.removeSpecialChars(a.index).toUpperCase()
          var y = self.removeSpecialChars(b.index).toUpperCase() 
          console.log(x,y)
          if(sortType === 1){
            if (x > y)
              return 1
            else 
              return -1
          } else {
            if(x < y) 
              return 1
            else 
              return -1
          }
        }
      })

      subheader.sort = -subheader.sort
      this.$set(this.structure, 'form_fields', sortObj)
    },



    removeSpecialChars(str) {
      return str.replace(/[^a-zA-Z0-9]+/g, "");
    },

    countDecisions(field) {
      let count = 0;
      for(let item of field.fields) {
        for(let subItem of item.fields) {
          if(subItem.name.split('_')[0] === 'quantity' && subItem.selected) {
            count += parseFloat(subItem.selected)
          }
        }
      }
      if(count === 0) {
        field.total = ''
      }
      else if(count < 0) {
        field.total = count.toPrecision(3)
      } else if(count > 999) {
        field.total = parseInt(count)
      } else {
        field.total = count.toPrecision(3)
      }
    },

    expandQuantity(field){
      let toShow = '';
      for(let item of field.fields) {
        for(let subItem of item.fields) {
          if(subItem.name.split('_')[0] === 'quantity' && subItem.selected) {
            toShow += item.label + ': ' + subItem.selected + '\n' 
          }
        }
      }
      return toShow
    },


    expandDecisions(field){
      let toShow = '';
      for(let item of field.fields) {
        for(let subItem of item.fields) {
          if(subItem.name.split('_')[0] === 'decision' && subItem.selected) {
            toShow += item.label + ': ' + subItem.selected + '\n' 
          }
        }
      }
      return toShow
    },



    doComments(comments_field) {
      let final_comments = ''
      for(let comment of comments_field) {
        if(comment.selected){
          final_comments += comment.label + ':' + comment.selected + '\n'
        }
      }
      return final_comments
    },

  },
}
</script>

<style lang="css" scoped>
  .blend {
    font-weight: bold;
  }

  td {
    text-align: center!important;
  }

  .small.but_big {
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
    transform:translateX(-50%);
  }
  .subheader th > div {
    position: relative;
    margin-bottom: .5rem;
  }

  .comments-section {
    position: absolute;
    right: .5rem;
    z-index: 1;
  }

  .submission-table tr td:last-of-type > * {
    max-width: 90%;
  }

  .fa-info-circle {
    margin-left: 5px;
  }
</style>