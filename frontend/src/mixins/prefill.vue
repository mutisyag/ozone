<script>
export default {

    name: 'prefill',

    data() {
        return {

        }
    },


    methods: {
        prefillSubstance(data, section) {
        	let group_field = {
		        label: 'test',
		        name: 'test',
		        substance: {
			            name: data.substance,
			            options: '',
			            selected: data.substance,
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
		                        label: 'Country of Destination of Exports**',
		                        name: 'destination_party',
		                        description: '',
		                        type: 'select',
		                        duplicate: false,
		                        selected: data.destination_party,
		                        options: null,
		                    },
		                    {
		                        label: 'Total Quantity Exported for All Uses',
		                        name: 'quantity_total_new',
		                        disabled: false,
		                        description: 'New',
		                        validation: 'numeric',
		                        type: 'number',
		                        selected: data.quantity_total_new,
		                    },
		                    {
		                        label: 'Total Quantity Exported for All Uses',
		                        name: 'quantity_total_recovered',
		                        description: 'Recovered and Reclaimed',
		                        disabled: false,
		                        type: 'number',
		                        validation: 'numeric',
		                        selected: data.quantity_total_recovered,
		                    },
		                    {
		                        label: 'Quantity of New Substances Exported as Feedstock',
		                        name: 'quantity_feedstock',
		                        description: '',
		                        disabled: false,
		                        type: 'number',
		                        validation: 'numeric',
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
	        	}
	        	section.push(group_field)
        },
    },

}
</script>
<style lang="css" scoped>
</style>