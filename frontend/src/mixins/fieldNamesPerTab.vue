<script>
export default {

    methods: {
        getCountryField(currentSection) {
            switch (currentSection) {
                case 'export_question':
                    return 'destination_party'
                    break;
                case 'import_question':
                    return 'source_party'
                    break;
                default:
                    // statements_def
                    break;
            }
        },

        getCountryLabel(currentSection) {
            switch (currentSection) {
                case 'export_question':
                    return 'Country of Destination of Exports**'
                    break;
                case 'import_question':
                    return 'Country of Destination of Imports**'
                    break;
                default:
                    // statements_def
                    break;
            }
        },

        getInnerFields(section, group) {
          let baseInnerFields = [
              {
                label: this.getCountryLabel(this.currentSection),
                name: this.getCountryField(this.currentSection),
                description: '',
                type: 'select',
                duplicate: true,
                selected: null,
                options: this.countryOptions,
              },
              {
                label: 'Total Quantity Exported for All Uses',
                name: 'quantity_total_new',
                disabled: false,
                description: 'New',
                validation: 'required',
                type: 'number',
                selected: null,
              },
              {
                label: 'Total Quantity Exported for All Uses',
                name: 'quantity_total_recovered',
                description: 'Recovered and Reclaimed',
                disabled: false,
                type: 'number',
                validation: 'required',
                selected: null,
              },
              {
                label: 'Quantity of New Substances Exported as Feedstock',
                name: 'quantity_feedstock',
                description: '',
                disabled: false,
                type: 'number',
                validation: 'required',
                selected: null,
              },
              {
                label: 'Quantity of New Substances Exported for Exempted Essential and Critical Uses*',
                name: 'quantity_exempted',
                name_type: 'type_exempted',
                total_type: null,
                disabled: false,
                modalShow: false,
                description: 'Quantity',
                total: 0,
                type: 'multiple_fields',
                fields: [
                  {
                    label: 'Essential use, other than L&A',
                    name: 'quantity_essential_uses',
                    fields: [
                      {
                        label: "Quantity in metric",
                        name: "quantity_essential_uses",
                        validation: 'numeric',
                        selected: null,
                        type: "number",
                      },
                      {
                        label: "Decision",
                        name: "decision_essential_uses",
                        selected: '',
                        type: "text",
                      }
                    ]
                  }, 
                  {
                    label: 'Critical use',
                    name: 'quantity_critical_uses',
                    fields: [
                      {
                        label: "Quantity in metric",
                        name: "quantity_critical_uses",
                        validation: 'numeric',
                        selected: null,
                        type: "number",
                      },
                      {
                        label: "Decision",
                        name: "decision_critical_uses",
                        selected: '',
                        type: "text",
                      }
                    ]
                  }, 
                  {
                    label: 'High ambient temperature',
                    name: 'high_ambient_temperature',
                    fields: [
                      {
                        label: "Quantity in metric",
                        name: "quantity_high_ambient_temperature",
                        validation: 'numeric',
                        selected: null,
                        type: "number",
                      },
                      {
                        label: "Decision",
                        name: "decision_high_ambient_temperature",
                        selected: '',
                        type: "text",
                      }
                    ]
                  }, 
                  {
                      label: 'Process agent uses',
                      name: 'process_agent_uses',
                      fields: [
                        {
                          label: "Quantity in metric",
                          name: "quantity_process_agent_uses",
                          selected: null,
                          type: "text",
                        },
                        {
                          label: "Decision",
                          name: "decision_process_agent_uses",
                          selected: '',
                          type: "text",
                        }
                      ]
                    }, 
                  {
                    label: 'Laboratory and analytical',
                    name: 'laboratory_analytical_uses',
                    fields: [
                      {
                        label: "Quantity in metric",
                        validation: 'numeric',
                        name: "quantity_laboratory_analytical_uses",
                        selected: null,
                        type: "number",
                      },
                      {
                        label: "Decision",
                        name: "decision_laboratory_analytical_uses",
                        selected: '',
                        type: "text",
                      }
                    ]
                  }, 
                  {
                    label: 'Quarantine and pre-shipment applications',
                    name: 'quarantine_pre_shipment',
                    fields: [
                      {
                        label: "Quantity in metric",
                        validation: 'numeric',
                        name: "quantity_quarantine_pre_shipment",
                        selected: null,
                        type: "number",
                      },
                      {
                        label: "Decision",
                        name: "decision_quarantine_pre_shipment",
                        selected: '',
                        type: "text",
                      }
                    ]
                  }, 
                   {
                    label: 'Other/Unspecified',
                    name: 'other',
                    fields: [
                      {
                        label: "Quantity in metric",
                        validation: 'numeric',
                        name: "quantity_other",
                        selected: null,
                        type: "number",
                      },
                      {
                        label: "Decision",
                        name: "decision_other",
                        selected: '',
                        type: "text",
                      }
                    ]
                  }, 
                ]
              },
            ]


          switch (section) {
            case 'export_question':
              return baseInnerFields
              break;
            case 'import_question':
              return baseInnerFields
              break;
            case 'production_question':
            return  [
           
              {
                label: 'Total production for all uses',
                name: 'quantity_total_produced',
                disabled: false,
                // description: 'New',
                validation: 'required',
                type: 'number',
                selected: null,
              },
              {
                label: 'Production for feedstock uses within your country',
                name: 'quantity_feedstock',
                disabled: false,
                type: 'number',
                validation: 'required',
                selected: null,
              },
              {
                label: 'Production for exempted essential, critical or other uses within your country**',
                name: 'quantity_exempted',
                name_type: 'type_exempted',
                total_type: null,
                disabled: false,
                modalShow: false,
                description: 'Quantity',
                total: 0,
                type: 'multiple_fields',
                fields: [
                  {
                    label: 'Essential use, other than L&A',
                    name: 'quantity_essential_uses',
                    fields: [
                      {
                        label: "Quantity in metric",
                        name: "quantity_essential_uses",
                        validation: 'numeric',
                        selected: null,
                        type: "number",
                      },
                      {
                        label: "Decision",
                        name: "decision_essential_uses",
                        selected: '',
                        type: "text",
                      }
                    ]
                  }, 
                  {
                    label: 'Critical use',
                    name: 'quantity_critical_uses',
                    fields: [
                      {
                        label: "Quantity in metric",
                        name: "quantity_critical_uses",
                        validation: 'numeric',
                        selected: null,
                        type: "number",
                      },
                      {
                        label: "Decision",
                        name: "decision_critical_uses",
                        selected: '',
                        type: "text",
                      }
                    ]
                  }, 
                  {
                    label: 'High ambient temperature',
                    name: 'high_ambient_temperature',
                    fields: [
                      {
                        label: "Quantity in metric",
                        name: "quantity_high_ambient_temperature",
                        validation: 'numeric',
                        selected: null,
                        type: "number",
                      },
                      {
                        label: "Decision",
                        name: "decision_high_ambient_temperature",
                        selected: '',
                        type: "text",
                      }
                    ]
                  }, 
                  {
                      label: 'Process agent uses',
                      name: 'process_agent_uses',
                      fields: [
                        {
                          label: "Quantity in metric",
                          name: "quantity_process_agent_uses",
                          selected: null,
                          type: "text",
                        },
                        {
                          label: "Decision",
                          name: "decision_process_agent_uses",
                          selected: '',
                          type: "text",
                        }
                      ]
                    }, 
                  {
                    label: 'Laboratory and analytical',
                    name: 'laboratory_analytical_uses',
                    fields: [
                      {
                        label: "Quantity in metric",
                        validation: 'numeric',
                        name: "quantity_laboratory_analytical_uses",
                        selected: null,
                        type: "number",
                      },
                      {
                        label: "Decision",
                        name: "decision_laboratory_analytical_uses",
                        selected: '',
                        type: "text",
                      }
                    ]
                  }, 
                  {
                    label: 'Quarantine and pre-shipment applications',
                    name: 'quarantine_pre_shipment',
                    fields: [
                      {
                        label: "Quantity in metric",
                        validation: 'numeric',
                        name: "quantity_quarantine_pre_shipment",
                        selected: null,
                        type: "number",
                      },
                      {
                        label: "Decision",
                        name: "decision_quarantine_pre_shipment",
                        selected: '',
                        type: "text",
                      }
                    ]
                  }, 
                   {
                    label: 'Other/Unspecified',
                    name: 'other',
                    fields: [
                      {
                        label: "Quantity in metric",
                        validation: 'numeric',
                        name: "quantity_other",
                        selected: null,
                        type: "number",
                      },
                      {
                        label: "Decision",
                        name: "decision_other",
                        selected: '',
                        type: "text",
                      }
                    ]
                  }, 
                ]
              },
              {
                label: 'Production for supply to Article 5 countries in accordance with Articles 2A 2H and 5',
                name: 'quantity_article_5',
                disabled: ['A','B'].includes(group.split('I')[0]) ? true : false,
                // description: 'New',
                validation: ['A','B'].includes(group.split('I')[0]) ? false : 'required',
                type: 'number',
                selected: null,
              },
            ]

              break;
            case 'destruction_question':
            return [
              {
                label: 'Quantity Destroyed',
                name: 'quantity_destroyed',
                disabled: false,
                // description: 'New',
                validation: 'required',
                type: 'number',
                selected: null,
              },
              {
                name: 'remarks_party',
                selected: '',
                type: 'textarea',
                label: 'Remarks (Secretariat)',
              },
              {
                name: 'remarks_os',
                selected: '',
                type: 'textarea',
                label: 'Remarks (Secretariat)',
              },
            ]
            break;
            default:
              // statements_def
              break;
          }
        }
    },


}
</script>