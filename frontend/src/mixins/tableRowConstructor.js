
import labels from '@/assets/labels'
export default {
   
        getCountryField(currentSection) {
            switch (currentSection) {
                case 'has_exports':
                    return 'destination_party'
                    break;
                case 'has_imports':
                    return 'source_party'
                    break;
                default:
                    // statements_def
                    break;
            }
        },

        getCountryLabel(currentSection) {
            switch (currentSection) {
                case 'has_exports':
                    return 'Country of Destination of Exports**'
                    break;
                case 'has_imports':
                    return 'Country of Destination of Imports**'
                    break;
                default:
                    // statements_def
                    break;
            }
        },

        createTooltip(fields, section){
          let tooltip_title = ''
          if(fields) {
            for(let field in fields) {
                tooltip_title += labels[section][field] + ': ' + fields[field] + '\n' 
            }
          }

          return tooltip_title
        },


        quantityCalculator(fields, parent, section) {
          let count = 0;
          let returnObj = {
            type: 'nonInput',
            selected: count,
          }

          let forTooltip = {}

          let quantities = fields 

          for(let quantity of quantities){
            if(parent[quantity].selected) {
              count += parseFloat(parent[quantity].selected) 
              forTooltip[quantity] = parent[quantity].selected
            }
          }

          if(count === 0) {
            returnObj.selected = ''
          }
          else if(count < 0) {
            returnObj.selected = count.toPrecision(3)
          } else if(count > 999) {
            returnObj.selected = parseInt(count)
          } else {
            returnObj.selected = count.toPrecision(3)
          }

          let tooltip = this.createTooltip(forTooltip,section)

          returnObj.tooltip = tooltip
          
          return returnObj
        },

        doSum(sumItems){
          return sumItems.reduce((sum,item) => {
            return this.valueConverter(item) + sum
          })
        },


        valueConverter(item) {
          if(item === null || item === undefined || isNaN(parseFloat(item))) {
            return 0
          } else {
            return parseFloat(item)
          }
        },



        decisionGenerator(fields, parent, section){
          let decisions = []
          let returnObj = {
            type: 'nonInput',
            selected: '',
          }
          let forTooltip = {}

          let decision_fields = fields

            for(let item of decision_fields) {
              if(parent[item].selected) {
                decisions.push(parent[item].selected)
                forTooltip[item] = parent[item].selected

              }
            }

          let tooltip = this.createTooltip(forTooltip,section)
          returnObj.tooltip = tooltip

          returnObj.selected = decisions.join(', ')
          return returnObj
        },

        getInnerFields(section, substance, group, country, blend, prefillData, ordering_id) {
          let self = this

          let countryFieldName = this.getCountryField(section)

          let baseInnerFields = {
            ordering_id: {selected: ordering_id || 0},
            substance: {
              type: 'select',
              selected: substance || null,
            },
            blend: {
              type: 'select',
              selected: blend || null,
              expand: false,
            },
            group: {
              selected: group,
            },
            quantity_total_new: {
              type: 'number',
              selected: null,
            },
            quantity_total_recovered: {
              type: 'number',
              selected: null,
            },
            quantity_feedstock: {
              type: 'number',
              selected: null,
            },
            get quantity_exempted() {
                let fields = ['quantity_essential_uses', 'quantity_critical_uses', 'quantity_high_ambient_temperature', 'quantity_process_agent_uses','quantity_laboratory_analytical_uses', 'quantity_quarantine_pre_shipment', 'quantity_other_uses']
                 return self.quantityCalculator(fields, this, section)
            },

            get decision_exempted() {
                let fields =  ['decision_essential_uses', 'decision_critical_uses', 'decision_high_ambient_temperature', 'decision_process_agent_uses','decision_laboratory_analytical_uses', 'decision_quarantine_pre_shipment', 'decision_other_uses']
                return self.decisionGenerator(fields, this, section)
            },
            quantity_essential_uses: {
              type: 'number',
              selected: null,
            },
            decision_essential_uses: {
              type: 'text',
              selected: '',
            },
            quantity_critical_uses: {
              type: 'number',
              selected: null,
            },
            decision_critical_uses: {
              type: 'text',
              selected: '',
            },
            quantity_high_ambient_temperature: {
              type: 'number',
              selected: null,
            },
            decision_high_ambient_temperature: {
              type: 'text',
              selected: '',
            },
            quantity_process_agent_uses: {
              type: 'number',
              selected: null,
            },
            decision_process_agent_uses: {
              type: 'text',
              selected: '',
            },
            quantity_laboratory_analytical_uses: {
              type: 'number',
              selected: null,
            },
            decision_laboratory_analytical_uses: {
              type: 'text',
              selected: '',
            },
            quantity_quarantine_pre_shipment: {
              type: 'number',
              selected: null,
            },
            decision_quarantine_pre_shipment: {
              type: 'text',
              selected: '',
            },
            quantity_other_uses: {
              type: 'number',
              selected: null,
            },
            decision_other_uses: {
              type: 'text',
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
              console.log(self.doSum([this.quantity_total_new.selected, this.quantity_total_recovered.selected]))
              if(self.doSum([this.quantity_total_new.selected, this.quantity_total_recovered.selected]) <= 0){
                errors.push('Total quantity imported for all uses is required')
              }


              if(self.valueConverter(this.quantity_exempted.selected) > self.doSum([this.quantity_total_new.selected, this.quantity_total_recovered.selected])) {
                errors.push('Total quantity imported for all uses must be >= to the sum of individual components')
              }


              let returnObj = {
                type: 'nonInput',
                selected: errors
              }

              return returnObj
            },
          }

          baseInnerFields[countryFieldName] = {
            type: 'multiselect',
            selected: country || null,
          }

          switch (section) {
            case 'has_exports':
              if(prefillData) {
                for(let field in prefillData){
                  baseInnerFields.hasOwnProperty(field) ? baseInnerFields[field].selected = prefillData[field] : null
                }
              }
              return baseInnerFields
              break;
            case 'has_imports':
              if(prefillData) {
                for(let field in prefillData){
                  baseInnerFields.hasOwnProperty(field) ? baseInnerFields[field].selected = prefillData[field] : null
                }
              }
              return baseInnerFields
              break;
            case 'has_produced':
              baseInnerFields = {
                  ordering_id: {selected: ordering_id || 0},
                  remarks_party: {
                     type: 'textarea',
                     selected: '',
                  },
                  remarks_os: {
                     type: 'textarea',
                     selected: '',
                  },
                  group: {
                    selected: group,
                  },
                  get quantity_exempted() {
                     let fields = ['quantity_critical_uses', 'quantity_essential_uses', 'quantity_high_ambient_temperature', 'quantity_laboratory_analytical_uses', 'quantity_process_agent_uses', 'quantity_quarantine_pre_shipment']
                      return self.quantityCalculator(fields, this, section)
                  },                               
                  get decision_exempted() {
                     let fields = ['decision_critical_uses', 'decision_essential_uses', 'decision_high_ambient_temperature', 'decision_laboratory_analytical_uses', 'decision_process_agent_uses', 'decision_quarantine_pre_shipment']
                      return self.decisionGenerator(fields, this, section)
                  },
                  quantity_critical_uses: {
                     type: 'number',
                     selected: null,
                  },
                  decision_critical_uses: {
                     type: 'text',
                     selected: '',
                  },
                  blend: {
                     type: 'select',
                     selected: blend || null,
                     expand: false,
                  },
                  quantity_essential_uses: {
                     type: 'number',
                     selected: null,
                  }, 
                  decision_essential_uses: {
                     type: 'text',
                     selected: '',
                  },
                  quantity_high_ambient_temperature: {
                     type: 'number',
                     selected: null,
                  },
                  decision_high_ambient_temperature: {
                     type: 'text',
                     selected: '',
                  },
                  quantity_laboratory_analytical_uses: {
                     type: 'number',
                     selected: null,
                  },
                  decision_laboratory_analytical_uses: {
                     type: 'text',
                     selected: '',
                  },
                  quantity_process_agent_uses: {
                     type: 'number',
                     selected: null,
                  }, 
                  decision_process_agent_uses: {
                     type: 'text',
                     selected: '',
                  },
                  quantity_quarantine_pre_shipment: {
                     type: 'number',
                     selected: null,
                  },
                  decision_quarantine_pre_shipment: {
                     type: 'text',
                     selected: '',
                  },
                  quantity_total_produced: {
                     type: 'number',
                     selected: null,
                  },
                  quantity_feedstock: {
                     type: 'number',
                     selected: null,
                     colspan: 2,
                  },
                  quantity_for_destruction: {
                    type: 'number',
                    selected: null,
                  },
                  quantity_article_5: {
                     type: 'text',
                     selected: null,
                  },
                  substance: {
                     type: 'select',
                     selected: substance || null,
                  },
                  get validation() {
                     let errors = []
                     if(!this.substance.selected){
                        errors.push('eroare1')
                     }

                     let returnObj = {
                        type: 'nonInput',
                        selected: errors
                     }

                     return returnObj
                  },
               };

              if(prefillData) {
                for(let field in prefillData){
                  baseInnerFields.hasOwnProperty(field) ? baseInnerFields[field].selected = prefillData[field] : null
                }
              }
               return baseInnerFields
               break;
            case 'has_destroyed':
            baseInnerFields = {
                  ordering_id: {selected: ordering_id || 0},
                  substance: {
                     type: 'select',
                     selected: substance || null,
                  }, 
                  quantity_destroyed: {
                     type: 'number',
                     selected: null,
                  },
                  group: {
                    selected: group
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
                     if(!this.substance.selected){
                        errors.push('eroare1')
                     }

                     let returnObj = {
                        type: 'nonInput',
                        selected: errors
                     }

                     return returnObj
                  },
            }
            if(prefillData) {
                for(let field in prefillData){
                  baseInnerFields.hasOwnProperty(field) ? baseInnerFields[field].selected = prefillData[field] : null
                }
              }
            return baseInnerFields
            break;
            case 'has_nonparty':
               baseInnerFields = {
                  ordering_id: {selected: ordering_id || 0},
                  remarks_party: {
                     type: 'textarea',
                     selected: '',
                  },
                  remarks_os: {
                     type: 'textarea',
                     selected: '',
                  },
                  quantity_import_new: {
                     type: 'text',
                     selected: null,
                  },
                  quantity_import_recovered: {
                     type: 'text',
                     selected: null,
                  },
                  quantity_export_new: {
                     type: 'text',
                     selected: null,
                  },
                  quantity_export_recovered: {
                     type: 'text',
                     selected: null,
                  },
                  substance: {
                     type: 'select',
                     selected: substance || null,
                  },
                  blend: {
                     type: 'select',
                     selected: blend || null,
                     expand: false,
                  },
                  group: {
                    selected:group
                  },
                  trade_party: {
                     type: 'multiselect',
                     selected: country || null,
                  },
                  get validation() {
                     let errors = []
                     if(!this.quantity_export_new.selected){
                        errors.push('eroare1')
                     }

                     let returnObj = {
                        type: 'nonInput',
                        selected: errors
                     }

                     return returnObj
                  },
               }
                if(prefillData) {
                  for(let field in prefillData){
                    baseInnerFields.hasOwnProperty(field) ? baseInnerFields[field].selected = prefillData[field] : null
                  }
                }
               return baseInnerFields;
               break;
            default:
              // statements_def
              break;
            }
         } 

}
