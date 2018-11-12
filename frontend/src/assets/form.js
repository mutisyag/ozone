import { intro_fields, reporting_party, substanceMaker } from './questionnaire_fields.js';

var form = {
    tabs: {
        sub_info: {
            intro: 'Respondents are requested to read the Introduction in section 2, the General Instructions in section 4 and the Definitions in section 5 carefully before proceeding to the questionnaire and to refer to them as necessary when completing the data forms.',
            title: 'Questionnaire',
            name: 'sub_info',
            isInvalid: false,
            party: {
                label: 'Party',
                name: 'party',
                selected: 'China',
                type: 'text',
                validation: 'required',
                disabled: true,
            },
            reporting_year: {
                label: 'Reporting Period',
                name: 'reporting_year',
                selected: '2016',
                type: 'text',
                validation: 'required',
                disabled: true,
            },
            description: '',
            // used for identification when adding labels
            name: 'form_intro',
            form_fields: reporting_party
        },
        tab_1: {
            intro: 'Respondents are requested to read the Introduction in section 2, the General Instructions in section 4 and the Definitions in section 5 carefully before proceeding to the questionnaire and to refer to them as necessary when completing the data forms.',
            title: 'Questionnaire',
            name: 'questionaire_questions',
            isInvalid: false,
            party: {
                label: 'Party',
                name: 'party',
                selected: 'China',
                type: 'text',
                validation: 'required',
                disabled: true,
            },
            reporting_year: {
                label: 'Reporting Period',
                name: 'reporting_year',
                selected: '2016',
                type: 'text',
                validation: 'required',
                disabled: true,
            },
            description: '',
            // used for identification when adding labels
            form_fields: intro_fields
        },
        tab_3: {
            status: null,
            saving: false,
            intro: '1. Fill in this form only if your country imported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide',
            title: 'Data on exports',
            name: 'has_exports',
            subtitle: 'in metric tonnes (not ODP tonnes)',
            description: 'Annexes A, B, C and E substances',
            isInvalid: false,
            section_subheaders: [{
                    label: "1",
                    name: 'substances',
                    sort: 1,
                    type: 'string',
                },
                {
                    label: "2",
                    name: 'destination_party',
                    sort: 1,
                    type: 'string',
                    tooltip: 'Applicable to all substances, including those contained in mixtures and blends.',
                },
                {
                    label: "New <br> 3",
                    name: 'quantity_total_new',
                    sort: 1,
                    type: 'number',
                },
                {
                    label: "Recovered and Reclaimed <br> 4",
                    name: 'quantity_total_recovered',
                    sort: 1,
                    type: 'number',
                },
                {
                    label: "<br> 5",
                    name: 'quantity_feedstock',
                    sort: 1,
                    type: 'number',
                },
                {
                    label: "Quantity <br> 6",
                    name: 'quantity_exempted',
                    sort: 1,
                    type: 'number',
                },
                {
                    label: "Decision / type of use**** or Remark <br> 7",
                    name: 'decision',
                },
                {
                    label: '8',
                    name: 'validation'
                },
            ],

            section_headers: [{
                    label: "Substances",
                },
                {
                    label: "Country of Destination of Exports",
                    tooltip: 'Applicable to all substances, including those contained in mixtures and blends.',
                },
                {
                    label: "Total Quantity Exported for All Uses",
                    colspan: 2,
                },
                {
                    label: "Quantity of New Substances Exported as Feedstock",
                    tooltip: 'Do not deduct from total production in column 3 of data form 3 (data on production).',
                },
                {
                    label: "Quantity of new substance exported for exempted essential, critical, high-ambient-temperature or other uses",
                    colspan: 2,
                    tooltip: 'Against each substance exported for exempted essential, critical, high-ambient-temperature or other uses, please specify the Meeting of the Parties decision that approved the use. Should the column space be insufficient, further information can be provided in the “comments” box above.',
                },
                {
                    label: "Status"
                }
            ],

            fields_order: ['substance','blend','destination_party','quantity_total_new','quantity_total_recovered','quantity_feedstock','quantity_exempted','decision_exempted', 'validation'],
            hidden_fields_order: ['quantity_essential_uses','decision_essential_uses','quantity_critical_uses','decision_critical_uses','quantity_high_ambient_temperature','decision_high_ambient_temperature','quantity_process_agent_uses','decision_process_agent_uses','quantity_laboratory_analytical_uses','decision_laboratory_analytical_uses','quantity_quarantine_pre_shipment','decision_quarantine_pre_shipment','quantity_other','decision_other'],
            modal_order: ['destination_party','quantity_total_new','quantity_total_recovered','quantity_feedstock'],
            form_fields: [],

            comments: [{
                    name: 'comments_party',
                    selected: '',
                    type: 'textarea',
                    label: 'Party Comments',
                },
                {
                    name: 'comments_secretariat',
                    selected: '',
                    type: 'textarea',
                    label: 'Secretariat Comments',
                },
            ],
            footnotes: ['[1] Tonne = Metric ton.'],
        },

        tab_2: {
            status: null,
            saving: false,
            intro: '1. Fill in this form only if your country imported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide',
            title: 'Data on imports',
            name: 'has_imports',
            comments: [{
                    name: 'comments_party',
                    selected: '',
                    type: 'textarea',
                    label: 'Party Comments',
                },
                {
                    name: 'comments_secretariat',
                    selected: '',
                    type: 'textarea',
                    label: 'Secretariat Comments',
                },
            ],
            subtitle: 'in metric tonnes (not ODP tonnes)',
            description: 'Annexes A, B, C and E substances',
            section_subheaders: [{
                    label: "1",
                    name: 'substances',
                    sort: 1,
                    type: 'string',
                },
                {
                    label: "2",
                    name: 'destination_party',
                    sort: 1,
                    type: 'string',
                    tooltip: 'Applicable to all substances, including those contained in mixtures and blends.',
                },
                {
                    label: "New <br> 3",
                    name: 'quantity_total_new',
                    sort: 1,
                    type: 'number',
                },
                {
                    label: "Recovered and Reclaimed <br> 4",
                    name: 'quantity_total_recovered',
                    sort: 1,
                    type: 'number',
                },
                {
                    label: "<br> 5",
                    name: 'quantity_feedstock',
                    sort: 1,
                    type: 'number',
                },
                {
                    label: "Quantity <br> 6",
                    name: 'quantity_exempted',
                    sort: 1,
                    type: 'number',
                },
                {
                    label: "Decision / type of use**** or Remark <br> 7",
                    name: 'decision',
                },
                {
                    label: "7",
                    name: "validation",
                },
            ],

            section_headers: [{
                    label: "Substances",
                },
                {
                    label: "Exporting party for quantities reported as imports",
                    tooltip: 'Applicable to all substances, including those contained in mixtures and blends.',
                },
                {
                    label: "Total Quantity Imported for All Uses",
                    colspan: 2,
                },
                {
                    label: "Quantity of New Substances Imported as Feedstock",
                    tooltip: 'Do not deduct from total production in column 3 of data form 3 (data on production).',
                },
                {
                    label: "Quantity of new substance imported for exempted essential, critical, high-ambient-temperature or other uses",
                    colspan: 2,
                    tooltip: 'Against each substance imported for exempted essential, critical, high-ambient-temperature or other uses, please specify the Meeting of the Parties decision that approved the use. Should the column space be insufficient, further information can be provided in the “comments” box above.',
                },
                {
                    label: "Status",
                },
            ],
            fields_order: ['substance','blend','source_party','quantity_total_new','quantity_total_recovered','quantity_feedstock','quantity_exempted','decision_exempted', 'validation'],
            hidden_fields_order: ['quantity_essential_uses','decision_essential_uses','quantity_critical_uses','decision_critical_uses','quantity_high_ambient_temperature','decision_high_ambient_temperature','quantity_process_agent_uses','decision_process_agent_uses','quantity_laboratory_analytical_uses','decision_laboratory_analytical_uses','quantity_quarantine_pre_shipment','decision_quarantine_pre_shipment','quantity_other','decision_other'],
            modal_order: ['source_party','quantity_total_new','quantity_total_recovered','quantity_feedstock'],
            form_fields: [],
            isInvalid: false,
            footnotes: ['[1] Tonne = Metric ton.'],
        },
        tab_4: {
            status: null,
            saving: false,
            intro: '1. Fill in this form only if your country imported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide',
            title: 'Data on production',
            name: 'has_produced',
            subtitle: 'in metric tonnes (not ODP tonnes)',
            isInvalid: false,
            description: 'Annexes A, B, C and E substances',
            form_fields: [],
            comments: '',

            fields_order: ['substance','blend','quantity_total_produced','quantity_feedstock','quantity_exempted','decision_exempted','quantity_article_5', 'validation'],
            
            hidden_fields_order: ['quantity_essential_uses','decision_essential_uses','quantity_critical_uses','decision_critical_uses','quantity_high_ambient_temperature','decision_high_ambient_temperature','quantity_process_agent_uses','decision_process_agent_uses','quantity_laboratory_analytical_uses','decision_laboratory_analytical_uses','quantity_quarantine_pre_shipment','decision_quarantine_pre_shipment','quantity_other','decision_other'],
            modal_order:  ['quantity_total_produced','quantity_feedstock','quantity_article_5'],


            section_subheaders: [
                {
                    label: "1",
                    name: 'substances',
                    sort: 1,
                    type: 'string',
                },
                {
                    label: "2",
                    name: 'quantity_total_produced',
                    sort: 1,
                    type: 'number',
                },
                {
                    label: "3",
                    name: 'quantity_feedstock',
                    sort: 1,
                    type: 'number',
                },
                {
                    label: "4 <br> Quantity",
                    name: 'quantity_feedstock',
                    sort: 1,
                    type: 'number',
                },
                {
                    label: "Decision / type of use <br> 5",
                    name: 'quantity_exempted',
                    sort: 1,
                    type: 'string',
                },
                {
                    label: "6",
                    name: "quantity_article_5",
                    sort: 1,
                    type: 'number'
                },
                {
                    label: "7",
                    name: "validation",
                },
            ],

            section_headers: [
                {
                    label: "Substances",
                },
                {
                    label: "Total production for all uses",
                },
                {
                    label: "Production for feedstock uses within your country",
                },
                {
                    label: "Production for exempted essential, critical or other uses within your country*",
                    colspan: 2,
                    tooltip: 'Against each substance produced for exempted essential, critical or other uses, please specify the Meeting of the Parties decision that approved the use. Should the column space be insufficient, further information can be provided in the “comments” box above.',
                },
                {
                    label: "Production for supply to Article 5 countries in accordance with Articles 2A 2H and 5"
                },
                {
                    label: "Status"
                }
            ],
            comments: [{
                    name: 'comments_party',
                    selected: '',
                    type: 'textarea',
                    label: 'Party Comments',
                },
                {
                    name: 'comments_secretariat',
                    selected: '',
                    type: 'textarea',
                    label: 'Secretariat Comments',
                },
            ],
        },
        tab_5: {
            status: null,
            saving: false,
            intro: '1. Fill in this form only if your country imported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide',
            title: 'Data on destruction',
            name: 'has_destroyed',
            subtitle: 'in metric tonnes (not ODP tonnes)',
            description: 'Annexes A, B, C and E substances',
            fields_order: [ "substance","blend" ,"quantity_destroyed", "remarks_party","remarks_os",'validation'],
            modal_order: [ "substance","blend" ,"quantity_destroyed"],
            isInvalid: false,
            form_fields: [],
            section_subheaders: [{
                    label: "1",
                    name: 'substances',
                    sort: 1,
                    type: 'string',
                },
                {
                    label: "2",
                    name: 'quantity_destroyed',
                    sort: 1,
                    type: 'number',
                },
                {
                    label: "3",
                    name: 'remarks_party',
                    sort: 1,
                    type: 'string',
                },
                {
                    label: "4",
                    name: 'remarks_os',
                    sort: 1,
                    type: 'string',
                },
                {
                    label: '5',
                    name: 'validation'
                },
            ],

            section_headers: [{
                    label: "Substances",
                },
                {
                    label: "Quantity destroyed",
                },
                {
                    label: "Remarks (party)",
                },
                {
                    label: "Remarks (Secretariat)"
                },
                {
                    label: "Status"
                }
            ],
        },
        tab_6: {
            status: null,
            saving: false,
            intro: '1. Fill in this form only if your country imported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide',
            title: 'Data on nonparty',
            name: 'has_nonparty',
            subtitle: 'in metric tonnes (not ODP tonnes)',
            description: 'Annexes A, B, C and E substances',
            isInvalid: false,


            fields_order: [ "substance","blend" ,"trade_party", "quantity_import_new","quantity_import_recovered",'quantity_export_new', 'quantity_export_recovered', 'remarks_party', 'remarks_os', 'validation'],
            
            modal_order: [ "substance","blend" ,"trade_party", "quantity_import_new","quantity_import_recovered",'quantity_export_new', 'quantity_export_recovered', 'validation'],

            // used for identification when adding labels
            form_fields: [],
            section_subheaders: [
                {
                    label: "1",
                    name: 'substances',
                    sort: 1,
                    type: 'string',
                },
                {
                    label: "2",
                    name: 'trade_party',
                    sort: 1,
                    type: 'string',
                },
                {
                    label: "New imports  <br> 3",
                    name: 'quantity_import_new',
                    sort: 1,
                    type: 'number',
                },
                {
                    label: "Recovered and reclaimed imports <br> 4",
                    name: 'quantity_import_recovered',
                    sort: 1,
                    type: 'number',
                },
                {
                    label: "New exports <br> 5",
                    name: 'quantity_export_new',
                    sort: 1,
                    type: 'number',
                },
                {
                    label: "Recovered and reclaimed exports <br> 6",
                    name: 'quantity_export_recovered',
                    sort: 1,
                    type: 'number',
                },
                {
                    label: "7",
                    name: 'remarks_party',
                    sort: 1,
                    type: 'string',
                },
                {
                    label: "8",
                    name: 'remarks_os',
                    sort: 1,
                    type: 'string',
                },
                {
                    label: '9',
                    name: 'validation',
                }
            ],

            section_headers: [
                {
                    label: "Substances",
                },
                {
                    label: "Exporting party for quantities reported as imports <br> <b>OR</b> <br> Country of destination of exports",
                },
                {
                    label: 'Quantity of imports from non-parties*',
                    colspan: 2,
                    tooltip: '* See definition of “non parties” in Instruction V.'
                },
                {
                    label: 'Quantity of exports to non-parties*',
                    colspan: 2,
                    tooltip: '* See definition of “non parties” in Instruction V.'
                },
                {
                    label: "Remarks (party)",
                },
                {
                    label: "Remarks (Secretariat)"
                },
                {
                    label: "Status"
                }
            ],

 
            comments: [{
                    name: 'comments_party',
                    selected: '',
                    type: 'textarea',
                    label: 'Party Comments',
                },
                {
                    name: 'comments_secretariat',
                    selected: '',
                    type: 'textarea',
                    label: 'Secretariat Comments',
                },
            ],
        },

        tab_7: {
            status: null,
            saving: false,
            intro: '1. Fill in this form only if your country generated HFC 23 from any facility that produced (manufactured)  Annex C Group I or Annex F substances ',
            title: 'Data on emissions',
            name: 'has_emissions',
            subtitle: 'in metric tonnes (not ODP tonnes)',
            description: 'Annexes A, B, C and E substances',
            isInvalid: false,
            // used for identification when adding labels
            form_fields: [],

            fields_order: ["facility_name","quantity_generated","quantity_feedstock","quantity_destroyed","quantity_emitted","remarks_party","remarks_os", 'validation'],

            section_subheaders: [{
                    label: "1",
                    name: 'facility_name',
                    sort: 1,
                    type: 'string',
                },
                {
                    label: "2",
                    name: 'quantity_generated',
                    sort: 1,
                    type: 'number',
                },
                {
                    label: "3",
                    name: 'quantity_feedstock',
                    sort: 1,
                    type: 'number',
                },
                {
                    label: "4",
                    name: 'quantity_destroyed',
                    sort: 1,
                    type: 'number',
                },
                {
                    label: "5",
                    name: 'quantity_emitted',
                    sort: 1,
                    type: 'number',
                },
                {
                    label: "6",
                    name: 'remarks_party',
                    sort: 1,
                    type: 'string',
                },
                {
                    label: "7",
                    name: 'remarks_os',
                    sort: 1,
                    type: 'string',
                },
                {
                    label: "8",
                    name: 'validation',
                }
            ],

            section_headers: [{
                    label: "Facility name or identifier",
                },
                {
                    label: "Amount [Generated]* <br> (tonnes)",
                    tooltip: "Amount [Generated] refers to amount that is captured, whether for destruction in another facility, feedstock or any other use. "
                },
                {
                    label: 'Amount Used for Feedstock** <br> (tonnes)',
                    tooltip: 'Amount converted to other substances shall be treated as feedstock uses.'
                },
                {
                    label: 'Amount Destroyed*** <br> (tonnes)',
                    tooltip: 'Amount Destroyed  refers to “Amount destroyed in the facility, with or without prior capture”'
                },
                {
                    label: 'Amount of Emissions <br> (tonnes)'
                },
                {
                    label: "Remarks (party)",
                },
                {
                    label: "Remarks (Secretariat)"
                },
                {
                    label: "Status"
                }
            ],
            comments: [{
                    name: 'comments_party',
                    selected: '',
                    type: 'textarea',
                    label: 'Party Comments',
                },
                {
                    name: 'comments_secretariat',
                    selected: '',
                    type: 'textarea',
                    label: 'Secretariat Comments',
                },
            ],
        },
        attachements: [{
                name: 'asd',
                url: 'www.google.com',
                id: 1,
            },
            {
                name: 'asd1',
                url: 'www.google.com',
                id: 2,
            },
            {
                name: 'asd2',
                url: 'www.google.com',
                id: 3,
            },
            {
                name: 'asd3',
                url: 'www.google.com',
                id: 4,
            },
        ],
    },
}
export default form