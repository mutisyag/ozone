<template>
  <div v-if="tab_info">
    <template slot="title">Title</template>
    <div class="form-sections">
      <table class="table">
        <thead>
          <tr class="first-header">
            <th v-for="header in info.section_1_headers" :colspan="header.colspan">
              <div v-if="header.tooltip" v-b-tooltip.hover placement="left" :title="header.tooltip">
                {{header.label}} <i class="fa fa-info-circle fa-lg"></i>
              </div>
              <div v-else>
                {{header.label}}
              </div>
            </th>
          </tr>
          <tr class="subheader">
            <th v-for="subheader in info.section_1_subheaders">
            <div style="cursor:pointer" v-if="subheader.sort" @click="sortTable(subheader.name, info.form_fields, subheader, subheader.type)">
              <span v-html="subheader.label"></span> <i v-if="subheader.sort" :class="setSortDirection(subheader.sort)"></i>
            </div>  
            <div v-else>
              <span v-html="subheader.label"></span>
            </div>
            </th>
          </tr>
        </thead>
        <tbody  v-for="(outer_field,outer_field_index) in info.form_fields" class="form-fields">
          <tr v-if="outer_field.name != 'blend'">
            <td style="padding-right: 2rem;">
              <div class="table-btn-group">
                <b-btn variant="info" @click="createModalData(outer_field.substance)">
                  Edit
                </b-btn>
                <b-btn variant="outline-danger" @click="remove_field(outer_field)" class="table-btn">Delete</b-btn>
              </div>
              <span v-b-tooltip.hover  placement="left" :title="outer_field.label" :class="outer_field.name">
                {{outer_field.substance.label}}
              </span>
            </td>
            <td v-for="(inner_field, inner_field_index) in outer_field.substance.inner_fields">
              <fieldGenerator v-if="inner_field.type != 'multiple_fields' && inner_field.name != 'country_of_destination_exports'" :disabled.sync="inner_field.disabled" :field.sync="inner_field"></fieldGenerator>
              <div v-else-if="inner_field.name === 'country_of_destination_exports' && !inner_field.selected">
                  <clonefield :current_field="outer_field" :inner_field="inner_field" :section="tab_info"></clonefield>
              </div>
              <div v-else-if="inner_field.name === 'country_of_destination_exports' && inner_field.selected">
                {{inner_field.selected}}
              </div>
              <div v-else>
                <div v-b-tooltip.hover placement="left" :title="expandQuantity(inner_field)" >
                  {{countDecisions(inner_field)}} {{inner_field.total}}
                </div>
              </div>
            </td>
            <td v-for="(inner_field, inner_field_index) in outer_field.substance.inner_fields" v-if="inner_field.type ==='multiple_fields'">
              <div v-b-tooltip.hover placement="left" :title="expandDecisions(inner_field)" >
                <div v-html="getDecisions(inner_field)"></div>
              </div>
              <div style="margin-left: -4rem;" v-for="quantity in inner_field.fields" class="special-field" v-if="outer_field.label === 'EI' && quantity.name === 'quarantine_pre_shipment_apl' && quantity.fields[0].selected" >
                <hr>
                Quantity of new {{outer_field.substance.label}} exported to be used for QPS applications
                <hr>
                <span>
                  {{quantity.fields[0].selected}}
                </span>
              </div>
              <span v-if="doComments(outer_field.substance.comments)" class="comments-section">
                <b-btn variant="link" class="comments-button" v-b-tooltip.hover  placement="left" :title="doComments(outer_field.substance.comments)" :id="`${outer_field.substance.name}_${outer_field_index}`">
                    <img class="icon" src="comments.svg">
                </b-btn>
              </span>
            </td>
          </tr>
          <tr v-else>
            <td class="blend-name" style="padding-right: .5rem; vertical-align: middle;">
              <div class="table-btn-group">
                <b-btn variant="info" @click="createModalData(outer_field.substance)">
                  Edit
                </b-btn>
                <b-btn variant="outline-danger" @click="remove_field(outer_field)" class="table-btn">Delete</b-btn>
              </div>
              <span style="cursor:pointer" @click="outer_field.expand = !outer_field.expand" v-b-tooltip.hover  placement="left" :title="outer_field.label" :class="outer_field.name">
                {{outer_field.substance.label}} <i :class="`fa fa-caret-square-o-${expandedStatus(outer_field.expand)}`"></i>
              </span>
            </td>
            <td v-for="(inner_field, inner_field_index) in outer_field.substance.inner_fields">
              <div  v-if="inner_field.type != 'multiple_fields' && inner_field.name != 'country_of_destination_exports'" >
                <fieldGenerator :disabled.sync="inner_field.disabled" :field.sync="inner_field"></fieldGenerator>
              </div>
              <div v-else-if="inner_field.name === 'country_of_destination_exports' && !inner_field.selected">
                  <clonefield :current_field="outer_field" :inner_field="inner_field" :section="tab_info"></clonefield>
              </div>
              <div v-else-if="inner_field.name === 'country_of_destination_exports' && inner_field.selected">
                {{inner_field.selected}}
              </div>
              <div v-else>
                <div v-b-tooltip.hover placement="left" :title="expandQuantity(inner_field)" >
                  {{countDecisions(inner_field)}} {{inner_field.total}}
                </div>
              </div>
            </td>

            <td v-for="(inner_field, inner_field_index) in outer_field.substance.inner_fields" v-if="inner_field.type ==='multiple_fields'">
              <div v-b-tooltip.hover placement="left" :title="expandDecisions(inner_field)" >
                <div v-html="getDecisions(inner_field)"></div>
              </div>
              <div style="margin-left: -4rem;" v-for="quantity in inner_field.fields" class="special-field" v-if="outer_field.label === 'B-Group I' && quantity.name === 'quarantine_pre_shipment_apl' && quantity.fields[0].selected" >
                <hr>
                Quantity of new {{outer_field.substance.label.label}} exported to be used for quarantine and pre shipment applications 
                <hr>
                <span>
                  {{quantity.fields[0].selected}}
                </span>
              </div>
              <span v-if="doComments(outer_field.substance.comments)" class="comments-section">
                <b-btn variant="link" class="comments-button" v-b-tooltip.hover  placement="left" :title="doComments(outer_field.substance.comments)" :id="`${outer_field.substance.name}_${outer_field_index}`">
                    <img class="icon" src="comments.svg">
                </b-btn>
              </span>
            </td>
          </tr>

          <tr v-for="substance in outer_field.substance.selected.composition" class="small" v-if="outer_field.expand">
            <td colspan="2">
              <div>
                <b-row>
                  <b-col>{{substance.name}}</b-col>
                  <b-col><b>{{substance.percent}}%</b></b-col>
                </b-row>
              </div>
            </td>
            <td :colspan="getSpanType(inner_field.type)" v-for="(inner_field, inner_field_index) in outer_field.substance.inner_fields" v-if="inner_field.name != 'country_of_destination_exports'">
              <div v-if="inner_field.type != 'multiple_fields' && inner_field.name != 'country_of_destination_exports'" >
                  <b-row v-if="splitBlend(inner_field.selected,substance.percent)">
                    <b-col> <b>{{splitBlend(inner_field.selected,substance.percent)}}</b></b-col>
                  </b-row>
              </div>
              <div v-else-if="inner_field.type ==='multiple_fields'">
                <div v-b-tooltip.hover placement="left" :title="expandQuantity(inner_field)" >
                  <b-row v-if="splitBlend(inner_field.total,substance.percent)">
                  <div style="display:none">{{countDecisions(inner_field)}}</div> 
                    <b-col><b>{{splitBlend(inner_field.total,substance.percent)}}</b></b-col>
                  </b-row>
                </div>
              </div>
              <div v-else></div>
            </td>
            <!-- <td>empty</td> -->
          </tr>

        </tbody>
      </table>
    </div>
    <div v-for="comment in info.comments" class="comments-input">
      <label>{{comment.label}}</label>
      <textarea class="form-control" v-model="comment.selected"></textarea>
    </div>
    <hr>
    <div class="footnotes">
      <p v-for="footnote in info.footnotes"><small>{{footnote}}</small></p>
    </div>

    <AppAside fixed>
      <DefaultAside :form="tab_info"> </DefaultAside>
    </AppAside>

    <b-modal size="lg" ref="edit_modal" id="edit_modal">
     <div v-if="modal_data" slot="modal-title">{{modal_data.label}}</div>
     <div v-if="modal_data">
       <b-row  v-if="!modal_data.selected.composition" >
         <b-col>
            <h6>Change substance</h6>
         </b-col>
         <b-col>
            <multiselect class="mb-2" label="text" track-by="text" placeholder="Select substance" v-model="modal_data.selected" :options="modal_data.options"></multiselect>
         </b-col>
       </b-row>

        <div :key="field.name" v-for="field in modal_data.inner_fields">
          <b-row v-if="field.type != 'multiple_fields'" >
            <b-col>{{field.label}}</b-col>
            <b-col >
                  <fieldGenerator :field.sync="field"></fieldGenerator>
            </b-col>
          </b-row>
          <b-row v-else v-for="inner_field of field.fields">
            <b-col lg="12"><b>{{inner_field.label}}</b></b-col>
            <b-col lg="6" v-for="sub_field in inner_field.fields">
                  <b-col>{{sub_field.label}}</b-col>
                   <b-col><fieldGenerator :field.sync="sub_field"></fieldGenerator></b-col>
            </b-col>
          </b-row>
          <hr>
        </div>
        <b-row class="mt-3" v-for="comment_field in modal_data.comments">
           <b-col lg="3">
              <h6>{{comment_field.label}}</h6>
           </b-col>
           <b-col lg="9">
              <textarea class="form-control"  v-model="comment_field.selected"></textarea>
           </b-col>
        </b-row>
     </div>
    </b-modal>
  </div>
</template>

<script>

import fieldGenerator from "./fieldGenerator"
import CloneFieldExports from './exports/CloneFieldExports.vue' 
import {Aside as AppAside} from '@coreui/vue'
import DefaultAside from './exports/DefaultAside'
import Multiselect from 'vue-multiselect'

export default {
  props: {
    info: Object,
  },

  created(){
    this.tab_info = this.info
  },

  components: {
    fieldGenerator: fieldGenerator, 
    AppAside, DefaultAside, Multiselect, 
    clonefield: CloneFieldExports 
  },

  data () {
    return {
      tab_info: null,
      modal_data: null,
      current_field: null,
      modal_comments: null,
    }
  },

  methods: {
    remove_field(parent, field) {
      this.info.form_fields.splice(this.info.form_fields.indexOf(parent), 1)
    },

    getDecisions(field){
      let decisions = []
      for(let item of field.fields) {
        let filtered = item.fields
                        .filter(inner_field => inner_field.name === 'decision' && inner_field.selected)
                        .map(field => field.selected) 
        decisions.push(filtered)
      }
      return decisions.filter( x => x[x.length - 1]).join(', ')
    },

    expandedStatus(status) {
      if(status) 
        return 'down'
      else 
        return 'left'
    },

    getSpanType(field_type) {
      if(field_type === 'multiple_fields'){
        return 2
      }
    }, 

    getSubheaderSpanType(field_name){
      if(field_name === 'substances' || field_name ==='quantity_import_exempted_essential_critical_uses')
        return 2
    },

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
            field.index = field.substance.label
          }
          else {
            field.index = ''
            for(let inner_field of field.substance.inner_fields) {
              if(value === 'country_of_destination_exports') {
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
      this.$set(this.info, 'form_fields', sortObj)
    },



    removeSpecialChars(str) {
      return str.replace(/[^a-zA-Z0-9]+/g, "");
    },

    countDecisions(field) {
      let count = 0;
      for(let item of field.fields) {
        for(let subItem of item.fields) {
          if(subItem.name === 'quantity_in_metric' && subItem.selected) {
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
          if(subItem.name === 'quantity_in_metric' && subItem.selected) {
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
          if(subItem.name === 'decision' && subItem.selected) {
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
  .AI {
    color: red;
  }

  .AII {
    color: blue;
  }

  .EI {
    color: green;
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
</style>