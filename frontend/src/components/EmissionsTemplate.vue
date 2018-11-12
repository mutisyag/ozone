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
	         <i style="
				    font-size: 2rem;
				    position: absolute;
				    cursor: pointer;
				    left: 17px;
				    margin-top: 1.5rem;" class="fa fa-plus-circle fa-lg" @click="addField"> </i>

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
        <tbody>
          <tr v-for="(row,row_index) in tab_info.form_fields" class="form-fields">
            <td v-for="(order, order_index) in tab_info.fields_order">
                <span v-b-tooltip.hover = "row[order].tooltip ? true : false" :title="row[order].tooltip" v-if="row[order].type === 'nonInput'">
                {{row[order].selected}}
              </span>
              <fieldGenerator v-else :field="row[order]"></fieldGenerator>
            </td>
	         <td class="row-controls visible">
	            <i class="fa fa-times-circle fa-lg" @click="remove_field(tab_info.form_fields, row)"></i>
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

  </div>
</template>

<script>

import fieldGenerator from "./fieldGenerator"
import CloneFieldExports from './exports/CloneFieldExports.vue' 
import Multiselect from 'vue-multiselect'

export default {
  props: {
    structure: Object,
    data: Object
  },

  created(){
    this.tab_info = this.structure
    this.tab_data = this.data
  },

  components: {
    fieldGenerator: fieldGenerator, 
    Multiselect, 
    clonefield: CloneFieldExports 
  },


  data () {
    return {
      tab_info: null,
      tab_data: null,
      modal_data: null,
      current_field: null,
      modal_comments: null,
    }
  },

  methods: {
    remove_field(field) {
      this.structure.form_fields.splice(this.structure.form_fields.indexOf(field), 1)
    },

    addField(){
    	let row = {
                    facility_name: {
                        type: 'text',
                        selected: '',
                    },
                  quantity_generated: {
                        type: 'number',    
                        selected: '',
                    },
                   quantity_feedstock: {
                        type: 'number',
                        selected: '',
                    },
                   quantity_destroyed: {
                        type: 'number',
                        selected: '',
                    },
                   quantity_emitted: {
                        type: 'number',
                        selected: '',
                    },
                    remarks_party: {
                     type: 'textarea',
                       selected: '',
                    },
                    remarks_os: {
                       type: 'textarea',
                       selected: '',
                    },
                    get validation() {
                     let errors = []
                     if(!this.facility_name.selected){
                        errors.push('eroare1')
                     }

                     let returnObj = {
                        type: 'nonInput',
                        selected: errors
                     }

                     return returnObj
                  },
                }
                this.structure.form_fields.push(row)
    },

    expandedStatus(status) {
      if(status) 
        return 'down'
      else 
        return 'left'
    },


    getSubheaderSpanType(field_name){
      if(field_name === 'substances' || field_name ==='quantity_exempted')
        return 2
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

  },
}
</script>

<style lang="css" scoped>
	.form-fields td:first-of-type{
		padding-left: 2rem;
	}
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


  .fa-info-circle {
    margin-left: 5px;
  }

  .row-controls {
  	margin-top: 15px;
  	position: absolute;
    left: 17px;
    width: 30px;
    background: none!important;
    padding: 0;
  }

  .row-controls i {
  	font-size: 1.5rem;
  	cursor: pointer;
  	margin-bottom: 5px;
  }

.first-header th:first-of-type {
	padding-left: 2rem;
}


</style>