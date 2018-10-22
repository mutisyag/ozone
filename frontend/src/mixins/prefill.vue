<template></template>
<script>
import fieldsPerTab from '@/mixins/fieldNamesPerTab.vue'
export default {
mixins: [fieldsPerTab],

methods: {


     prefillSubstance(tab_name, data, section, countryOptions, current_country, substance, substances) {
        let group_field = tab_name != 'has_emissions' ? {
            label: substance.group.group_id,
            name: substance.group.group_id,
            substance: {
                name: substance.value,
                options: substances,
                selected: substance,
                comments: [{
                        name: "remarks_party",
                        label: "Remarks (party)",
                        selected: data.remarks_party,
                        type: "text",
                    },
                    {
                        name: "remarks_os",
                        selected: data.remarks_os,
                        type: "text",
                        label: "Remarks (Secretariat)",
                    },
                ],
                inner_fields: [{
                        label: this.getCountryLabel(tab_name),
                        name: this.getCountryField(tab_name),
                        description: '',
                        type: 'select',
                        duplicate: true,
                        selected: current_country,
                    },
                    {
                        label: 'Total Quantity Exported for All Uses',
                        name: 'quantity_total_new',
                        disabled: false,
                        description: 'New',
                        validation: 'required',
                        type: 'number',
                        selected: data.quantity_total_new,
                    },
                    {
                        label: 'Total Quantity Exported for All Uses',
                        name: 'quantity_total_recovered',
                        description: 'Recovered and Reclaimed',
                        disabled: false,
                        type: 'number',
                        validation: 'required',
                        selected: data.quantity_total_recovered,
                    },
                    {
                        label: 'Quantity of New Substances Exported as Feedstock',
                        name: 'quantity_feedstock',
                        description: '',
                        disabled: false,
                        type: 'number',
                        validation: 'required',
                        selected: data.quantity_feedstock,
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
                        fields: [{
                                label: 'Essential use, other than L&A',
                                name: 'quantity_essential_uses',
                                fields: [{
                                        label: "Quantity in metric",
                                        name: "quantity_essential_uses",
                                        validation: 'numeric',
                                        selected: data.quantity_essential_uses,
                                        type: "number",
                                    },
                                    {
                                        label: "Decision",
                                        name: "decision_essential_uses",
                                        selected: data.decision_essential_uses,
                                        type: "text",
                                    }
                                ]
                            },
                            {
                                label: 'Critical use',
                                name: 'quantity_critical_uses',
                                fields: [{
                                        label: "Quantity in metric",
                                        name: "quantity_critical_uses",
                                        validation: 'numeric',
                                        selected: data.quantity_critical_uses,
                                        type: "number",
                                    },
                                    {
                                        label: "Decision",
                                        name: "decision_critical_uses",
                                        selected: data.decision_critical_uses,
                                        type: "text",
                                    }
                                ]
                            },
                            {
                                label: 'High ambient temperature',
                                name: 'high_ambient_temperature',
                                fields: [{
                                        label: "Quantity in metric",
                                        name: "quantity_high_ambient_temperature",
                                        validation: 'numeric',
                                        selected: data.quantity_high_ambient_temperature,
                                        type: "number",
                                    },
                                    {
                                        label: "Decision",
                                        name: "decision_high_ambient_temperature",
                                        selected: data.decision_high_ambient_temperature,
                                        type: "text",
                                    }
                                ]
                            },
                            {
                                label: 'Process agent uses',
                                name: 'process_agent_uses',
                                fields: [{
                                        label: "Quantity in metric",
                                        name: "quantity_process_agent_uses",
                                        selected: data.quantity_process_agent_uses,
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
                                fields: [{
                                        label: "Quantity in metric",
                                        validation: 'numeric',
                                        name: "quantity_laboratory_analytical_uses",
                                        selected: data.quantity_laboratory_analytical_uses,
                                        type: "number",
                                    },
                                    {
                                        label: "Decision",
                                        name: "decision_laboratory_analytical_uses",
                                        selected: data.decision_laboratory_analytical_uses,
                                        type: "text",
                                    }
                                ]
                            },
                            {
                                label: 'Quarantine and pre-shipment applications',
                                name: 'quarantine_pre_shipment',
                                fields: [{
                                        label: "Quantity in metric",
                                        validation: 'numeric',
                                        name: "quantity_quarantine_pre_shipment",
                                        selected: data.quantity_quarantine_pre_shipment,
                                        type: "number",
                                    },
                                    {
                                        label: "Decision",
                                        name: "decision_quarantine_pre_shipment",
                                        selected: data.decision_quarantine_pre_shipment,
                                        type: "text",
                                    }
                                ]
                            },
                            {
                                label: 'Other/Unspecified',
                                name: 'other',
                                fields: [{
                                        label: "Quantity in metric",
                                        validation: 'numeric',
                                        name: "quantity_other",
                                        selected: data.quantity_other,
                                        type: "number",
                                    },
                                    {
                                        label: "Decision",
                                        name: "decision_other",
                                        selected: data.decision_other,
                                        type: "text",
                                    }
                                ]
                            },
                        ]
                    },
                ]
            }
        } : null

        if(tab_name === 'has_produced') {
         group_field = {
            label: substance.group.group_id,
            name: substance.group.group_id,
            substance: {
                name: substance.value,
                options: substances,
                selected: substance,
                comments: [{
                        name: "remarks_party",
                        label: "Remarks (party)",
                        selected: data.remarks_party,
                        type: "text",
                    },
                    {
                        name: "remarks_os",
                        selected: data.remarks_os,
                        type: "text",
                        label: "Remarks (Secretariat)",
                    },
                ],
                inner_fields: [
                      {
                        label: 'Total production for all uses',
                        name: 'quantity_total_produced',
                        disabled: false,
                        // description: 'New',
                        validation: 'required',
                        type: 'number',
                        selected: data.quantity_total_produced,
                      },
                      {
                        label: 'Production for feedstock uses within your country',
                        name: 'quantity_feedstock',
                        disabled: false,
                        type: 'number',
                        validation: 'required',
                        selected: data.quantity_feedstock,
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
                                selected: data.quantity_essential_uses,
                                type: "number",
                              },
                              {
                                label: "Decision",
                                name: "decision_essential_uses",
                                selected: data.decision_essential_uses,
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
                                selected: data.quantity_critical_uses,
                                type: "number",
                              },
                              {
                                label: "Decision",
                                name: "decision_critical_uses",
                                selected: data.decision_critical_uses,
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
                                selected: data.quantity_high_ambient_temperature,
                                type: "number",
                              },
                              {
                                label: "Decision",
                                name: "decision_high_ambient_temperature",
                                selected: data.decision_high_ambient_temperature,
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
                                  selected: data.quantity_process_agent_uses,
                                  type: "text",
                                },
                                {
                                  label: "Decision",
                                  name: "decision_process_agent_uses",
                                  selected: data.decision_process_agent_uses,
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
                                selected: data.quantity_laboratory_analytical_uses,
                                type: "number",
                              },
                              {
                                label: "Decision",
                                name: "decision_laboratory_analytical_uses",
                                selected: data.decision_laboratory_analytical_uses,
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
                                selected: data.quantity_quarantine_pre_shipment,
                                type: "number",
                              },
                              {
                                label: "Decision",
                                name: "decision_quarantine_pre_shipment",
                                selected: data.decision_quarantine_pre_shipment,
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
                                selected: data.quantity_other,
                                type: "number",
                              },
                              {
                                label: "Decision",
                                name: "decision_other",
                                selected: data.decision_other,
                                type: "text",
                              }
                            ]
                          }, 
                        ]
                      },
                      {
                        label: 'Production for supply to Article 5 countries in accordance with Articles 2A 2H and 5',
                        name: 'quantity_article_5',
                        disabled: ['A','B'].includes(substance.group.group_id.split('I')[0]) ? true : false,
                        // description: 'New',
                        validation: ['A','B'].includes(substance.group.group_id.split('I')[0]) ? false : 'required',
                        type: 'number',
                        selected: data.quantity_article_5,
                      },
                    ]

            }
        }
        }


          if(tab_name === 'has_destroyed') {
             group_field = {
                label: substance.group.group_id,
                name: substance.group.group_id,
                substance: {
                    name: substance.value,
                    options: substances,
                    selected: substance,
                    comments: [{
                            name: "remarks_party",
                            label: "Remarks (party)",
                            selected: data.remarks_party,
                            type: "text",
                        },
                        {
                            name: "remarks_os",
                            selected: data.remarks_os,
                            type: "text",
                            label: "Remarks (Secretariat)",
                        },
                    ],
                    inner_fields:[
                          {
                            label: 'Quantity Destroyed',
                            name: 'quantity_destroyed',
                            disabled: false,
                            // description: 'New',
                            validation: 'required',
                            type: 'number',
                            selected: data.quantity_destroyed,
                          },
                         {
                          name: 'comments_party',
                          selected: data.remarks_party,
                          type: 'textarea',
                          label: 'Remarks (Secretariat)',
                        },
                        {
                          name: 'comments_secretariat',
                          selected: data.remarks_os,
                          type: 'textarea',
                          label: 'Remarks (Secretariat)',
                        },
                    ]
                }
            }
        }

        if(tab_name === 'has_nonparty') {
            group_field = 

        group_field = {
                label: substance.group.group_id,
                name: substance.group.group_id,
                substance: {
                    name: substance.value,
                    options: substances,
                    selected: substance,
                    comments: null,
                    inner_fields:[
                                  {
                                    label: "Exporting party for quantities reported as imports OR Country of destination of exports",
                                    name: 'trade_party',
                                    description: '',
                                    type: 'select',
                                    duplicate: true,
                                    selected: null,
                                  },
                                  {
                                    label: 'Quantity of new imports from non-parties',
                                    name: 'quantity_import_new',
                                    disabled: false,
                                    // description: 'New',
                                    // validation: 'required',
                                    type: 'number',
                                    selected: data.quantity_import_new,
                                  },
                                  {
                                    label: 'Quantity of recovered and reclaimed imports from non-parties',
                                    name: 'quantity_import_recovered',
                                    disabled: false,
                                    // description: 'New',
                                    // validation: 'required',
                                    type: 'number',
                                    selected: data.quantity_import_recovered,
                                  },
                                  {
                                    label: 'Quantity of new exports to non-parties*',
                                    name: 'quantity_export_new',
                                    disabled: false,
                                    // description: 'New',
                                    // validation: 'required',
                                    type: 'number',
                                    selected: data.quantity_export_new,
                                  },
                                  {
                                    label: 'Quantity of recovered and reclaimed exports to non-parties',
                                    name: 'quantity_export_recovered',
                                    disabled: false,
                                    // description: 'New',
                                    // validation: 'required',
                                    type: 'number',
                                    selected: data.quantity_export_recovered,
                                  },
                                  {
                                    name: 'remarks_party',
                                    selected: data.remarks_party,
                                    type: 'textarea',
                                    label: 'Remarks (Secretariat)',
                                  },
                                  {
                                    name: 'remarks_os',
                                    selected: data.remarks_os,
                                    type: 'textarea',
                                    label: 'Remarks (Secretariat)',
                                  },
                                ]
                }
            }



        }

        if(tab_name === 'has_emissions') {
             group_field = [
                    {
                        name: 'facility_name',
                        type: 'text',
                        validation: 'required',
                        label: 'Facility name or identifier',
                        selected: data.facility_name,
                    },
                    {
                        name: 'quantity_generated',
                        type: 'number',
                        validation: 'required',
                        label: 'Amount [Generated]',
                        selected: data.quantity_generated,
                    },
                    {
                        name: 'quantity_feedstock',
                        type: 'number',
                        validation: 'required',
                        label: 'Amount Used for Feedstock',
                        selected: data.quantity_generated,
                    },
                    {
                        name: 'quantity_destroyed',
                        type: 'number',
                        validation: 'required',
                        label: 'Amount Destroyed',
                        selected: data.quantity_destroyed,
                    },
                    {
                        name: 'quantity_emitted',
                        type: 'number',
                        validation: 'required',
                        label: 'Amount of Emissions',
                        selected: data.quantity_emitted,
                    },
                    {
                        name: 'remarks_party',
                        selected: data.remarks_party,
                        type: 'textarea',
                        label: 'Party Comments',
                    },
                    {
                        name: 'remarks_os',
                        selected: data.remarks_os,
                        type: 'textarea',
                        label: 'Secretariat Comments',
                    },
                ]
        }

        section.push(group_field)
    }
}


}
</script>