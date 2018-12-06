import { intro_fields, reporting_party } from './questionnaire_fields.js'

const form = {
	tabs: {
		sub_info: {
			intro: 'Respondents are requested to read the Introduction in section 2, the General Instructions in section 4 and the Definitions in section 5 carefully before proceeding to the questionnaire and to refer to them as necessary when completing the data forms.',
			title: 'Questionnaire',
			isInvalid: false,
			party: {
				label: 'Party',
				name: 'party',
				selected: 'China',
				type: 'text',
				validation: 'required',
				disabled: true
			},
			reporting_year: {
				label: 'Reporting Period',
				name: 'reporting_year',
				selected: '2016',
				type: 'text',
				validation: 'required',
				disabled: true
			},
			description: '',
			// used for identification when adding labels
			name: 'form_intro',
			form_fields: reporting_party
		},
		questionaire_questions: {
			intro: 'Respondents are requested to read the Introduction in section 2, the General Instructions in section 4 and the Definitions in section 5 carefully before proceeding to the questionnaire and to refer to them as necessary when completing the data forms.',
			title: 'Questionnaire',
			name: 'questionaire_questions',
			status: null,
			isInvalid: false,
			description: '',
			// used for identification when adding labels
			form_fields: intro_fields
		},
		has_exports: {
			ordering_id: 0,
			status: null,
			saving: false,
			intro: '1. Fill in this form only if your country imported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide',
			title: 'Exports',
			name: 'has_exports',
			subtitle: 'in metric tonnes (not ODP tonnes)',
			description: 'Annexes A, B, C and E substances',
			isInvalid: false,
			section_subheaders: [{
				label: '1',
				name: 'substance',
				sort: 1,
				type: 'string'
			},
			{
				label: '2',
				name: 'destination_party',
				sort: 1,
				type: 'string',
				tooltip: 'Applicable to all substances, including those contained in mixtures and blends.'
			},
			{
				label: 'New <br> 3',
				name: 'quantity_total_new',
				sort: 1,
				type: 'number'
			},
			{
				label: 'Recovered and Reclaimed <br> 4',
				name: 'quantity_total_recovered',
				sort: 1,
				type: 'number'
			},
			{
				label: '<br> 5',
				name: 'quantity_feedstock',
				sort: 1,
				type: 'number'
			},
			{
				label: 'Quantity <br> 6',
				name: 'quantity_exempted',
				sort: 1,
				type: 'number'
			},
			{
				label: 'Decision / type of use**** or Remark <br> 7',
				name: 'decision_exempted'
			},
			{
				label: '8',
				name: 'validation'
			}
			],

			section_headers: [{
				label: 'Substances'
			},
			{
				label: 'Country of Destination of Exports',
				tooltip: 'Applicable to all substances, including those contained in mixtures and blends.'
			},
			{
				label: 'Total Quantity Exported for All Uses',
				colspan: 2
			},
			{
				label: 'Quantity of New Substances Exported as Feedstock',
				tooltip: 'Do not deduct from total production in column 3 of data form 3 (data on production).'
			},
			{
				label: 'Quantity of new substance exported for exempted essential, critical, high-ambient-temperature or other uses',
				colspan: 2,
				tooltip: 'Against each substance exported for exempted essential, critical, high-ambient-temperature or other uses, please specify the Meeting of the Parties decision that approved the use. Should the column space be insufficient, further information can be provided in the “comments” box above.'
			},
			{
				label: 'Status'
			}
			],

			blend_substance_headers: ['substance', 'percent', 'quantity_total_new', 'quantity_total_recovered', 'quantity_feedstock', 'quantity_exempted'],

			fields_order: ['substance', 'blend', 'destination_party', 'quantity_total_new', 'quantity_total_recovered', 'quantity_feedstock', 'quantity_exempted', 'decision_exempted', 'validation'],
			hidden_fields_order: ['quantity_essential_uses', 'decision_essential_uses', 'quantity_critical_uses', 'decision_critical_uses', 'quantity_high_ambient_temperature', 'decision_high_ambient_temperature', 'quantity_process_agent_uses', 'decision_process_agent_uses', 'quantity_laboratory_analytical_uses', 'decision_laboratory_analytical_uses', 'quantity_quarantine_pre_shipment', 'decision_quarantine_pre_shipment', 'quantity_other_uses', 'decision_other_uses'],
			modal_order: ['destination_party', 'quantity_total_new', 'quantity_total_recovered', 'quantity_feedstock'],
			form_fields: [],

			comments: [{
				name: 'comments_party',
				selected: '',
				type: 'textarea',
				label: 'Party Comments'
			},
			{
				name: 'comments_secretariat',
				selected: '',
				type: 'textarea',
				label: 'Secretariat Comments'
			}
			],
			footnotes: ['[1] Tonne = Metric ton.']
		},

		has_imports: {
			ordering_id: 0,
			status: null,
			saving: false,
			intro: '1. Fill in this form only if your country imported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide',
			title: 'Imports',
			name: 'has_imports',
			comments: [{
				name: 'comments_party',
				selected: '',
				type: 'textarea',
				label: 'Party Comments'
			},
			{
				name: 'comments_secretariat',
				selected: '',
				type: 'textarea',
				label: 'Secretariat Comments'
			}
			],
			subtitle: 'in metric tonnes (not ODP tonnes)',
			description: 'Annexes A, B, C and E substances',
			blend_substance_headers: ['substance', 'percent', 'quantity_total_new', 'quantity_total_recovered', 'quantity_feedstock', 'quantity_exempted'],
			section_subheaders: [{
				label: '1',
				name: 'substance',
				sort: 1,
				type: 'string'
			},
			{
				label: '2',
				name: 'source_party',
				sort: 1,
				type: 'string',
				tooltip: 'Applicable to all substances, including those contained in mixtures and blends.'
			},
			{
				label: 'New <br> 3',
				name: 'quantity_total_new',
				sort: 1,
				type: 'number'
			},
			{
				label: 'Recovered and Reclaimed <br> 4',
				name: 'quantity_total_recovered',
				sort: 1,
				type: 'number'
			},
			{
				label: '<br> 5',
				name: 'quantity_feedstock',
				sort: 1,
				type: 'number'
			},
			{
				label: 'Quantity <br> 6',
				name: 'quantity_exempted',
				sort: 1,
				type: 'number'
			},
			{
				label: 'Decision / type of use**** or Remark <br> 7',
				name: 'decision_exempted'
			},
			{
				label: '7',
				name: 'validation'
			}
			],

			section_headers: [{
				label: 'Substances'
			},
			{
				label: 'Exporting party for quantities reported as imports',
				tooltip: 'Applicable to all substances, including those contained in mixtures and blends.'
			},
			{
				label: 'Total Quantity Imported for All Uses',
				colspan: 2
			},
			{
				label: 'Quantity of New Substances Imported as Feedstock',
				tooltip: 'Do not deduct from total production in column 3 of data form 3 (data on production).'
			},
			{
				label: 'Quantity of new substance imported for exempted essential, critical, high-ambient-temperature or other uses',
				colspan: 2,
				tooltip: 'Against each substance imported for exempted essential, critical, high-ambient-temperature or other uses, please specify the Meeting of the Parties decision that approved the use. Should the column space be insufficient, further information can be provided in the “comments” box above.'
			},
			{
				label: 'Status'
			}
			],
			fields_order: ['substance', 'blend', 'source_party', 'quantity_total_new', 'quantity_total_recovered', 'quantity_feedstock', 'quantity_exempted', 'decision_exempted', 'validation'],
			hidden_fields_order: ['quantity_essential_uses', 'decision_essential_uses', 'quantity_critical_uses', 'decision_critical_uses', 'quantity_high_ambient_temperature', 'decision_high_ambient_temperature', 'quantity_process_agent_uses', 'decision_process_agent_uses', 'quantity_laboratory_analytical_uses', 'decision_laboratory_analytical_uses', 'quantity_quarantine_pre_shipment', 'decision_quarantine_pre_shipment', 'quantity_other_uses', 'decision_other_uses'],
			modal_order: ['source_party', 'quantity_total_new', 'quantity_total_recovered', 'quantity_feedstock'],
			form_fields: [],
			isInvalid: false,
			footnotes: ['[1] Tonne = Metric ton.']
		},
		has_produced: {
			ordering_id: 0,
			status: null,
			saving: false,
			intro: '1. Fill in this form only if your country imported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide',
			title: 'Production',
			name: 'has_produced',
			subtitle: 'in metric tonnes (not ODP tonnes)',
			isInvalid: false,
			description: 'Annexes A, B, C and E substances',
			form_fields: [],
			fields_order: ['substance', 'blend', 'quantity_total_produced', 'quantity_feedstock', 'quantity_exempted', 'decision_exempted', 'quantity_article_5', 'validation'],
			special_fields_order: ['substance', 'quantity_total_produced', 'quantity_feedstock', 'quantity_for_destruction', 'quantity_exempted', 'decision_exempted', 'quantity_article_5', 'validation'],
			hidden_fields_order: ['quantity_essential_uses', 'decision_essential_uses', 'quantity_critical_uses', 'decision_critical_uses', 'quantity_high_ambient_temperature', 'decision_high_ambient_temperature', 'quantity_process_agent_uses', 'decision_process_agent_uses', 'quantity_laboratory_analytical_uses', 'decision_laboratory_analytical_uses', 'quantity_quarantine_pre_shipment', 'decision_quarantine_pre_shipment', 'quantity_other_uses', 'decision_other_uses'],
			modal_order: ['quantity_total_produced', 'quantity_feedstock', 'quantity_article_5'],
			blend_substance_headers: ['substance', 'percent', 'quantity_total_produced', 'quantity_feedstock', 'quantity_exempted', 'quantity_article_5'],

			section_subheaders: [
				{
					label: '',
					name: 'substance',
					sort: 1,
					type: 'string'
				},
				{
					label: '2',
					name: 'quantity_total_produced',
					sort: 1,
					type: 'number'
				},
				{
					label: '3',
					name: 'quantity_feedstock',
					sort: 1,
					colspan: 2,
					type: 'number'
				},
				{
					label: 'Quantity <br> 5',
					name: 'quantity_exempted',
					sort: 1,
					type: 'string'
				},
				{
					label: 'Decision / type of use <br> 5',
					name: 'decision_exempted',
					sort: 1,
					type: 'string'
				},
				{
					label: '6',
					name: 'quantity_article_5',
					sort: 1,
					type: 'number'
				},
				{
					label: '7',
					name: 'validation'
				}
			],

			section_headers: [
				{
					label: 'Substances'
				},
				{
					label: 'Total production for all uses'
				},
				{
					label: 'Production for feedstock uses within your country'
				},
				{
					label: 'Production for exempted essential, critical or other uses within your country*',
					colspan: 2,
					tooltip: 'Against each substance produced for exempted essential, critical or other uses, please specify the Meeting of the Parties decision that approved the use. Should the column space be insufficient, further information can be provided in the “comments” box above.'
				},
				{
					label: 'Production for supply to Article 5 countries in accordance with Articles 2A 2H and 5'
				},
				{
					label: 'Status'
				}
			],

			special_headers: {

				section_headers: [
					{
						label: 'Substances'
					},
					{
						label: 'Total production for all uses'
					},
					{
						label: 'Production for feedstock uses within your country',
						colspan: 2
					},
					{
						label: 'Production for exempted essential, critical or other uses within your country*',
						colspan: 2,
						tooltip: 'Against each substance produced for exempted essential, critical or other uses, please specify the Meeting of the Parties decision that approved the use. Should the column space be insufficient, further information can be provided in the “comments” box above.'
					},
					{
						label: 'Production for supply to Article 5 countries in accordance with Articles 2A 2H and 5'
					},
					{
						label: 'Status'
					}
				],

				section_subheaders: [
					{
						label: '1',
						name: 'substances'
					},
					{
						label: '2.Captured for all uses',
						name: 'quantity_total_produced'
					},
					{
						label: '3a.Captured for feedstock uses within your country',
						name: 'quantity_feedstock'
					},
					{
						label: '3b.Captured for destruction***',
						name: 'quantity_for_destruction'
					},
					{
						label: 'Quantity <br> 5',
						name: 'quantity_exempted',
						sort: 1,
						type: 'string'
					},
					{
						label: 'Decision / type of use <br> 5',
						name: 'decision_exempted',
						sort: 1,
						type: 'string'
					},
					{
						label: '6',
						name: 'quantity_article_5',
						sort: 1,
						type: 'number'
					},
					{
						label: '7',
						name: 'validation'
					}
				]
			},

			comments: [{
				name: 'comments_party',
				selected: '',
				type: 'textarea',
				label: 'Party Comments'
			},
			{
				name: 'comments_secretariat',
				selected: '',
				type: 'textarea',
				label: 'Secretariat Comments'
			}
			]
		},
		has_destroyed: {
			ordering_id: 0,
			status: null,
			saving: false,
			intro: '1. Fill in this form only if your country imported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide',
			title: 'Destruction',
			name: 'has_destroyed',
			subtitle: 'in metric tonnes (not ODP tonnes)',
			description: 'Annexes A, B, C and E substances',
			fields_order: ['substance', 'quantity_destroyed', 'remarks_party', 'remarks_os', 'validation'],
			modal_order: ['quantity_destroyed'],
			isInvalid: false,
			form_fields: [],
			section_subheaders: [{
				label: '1',
				name: 'substance',
				sort: 1,
				type: 'string'
			},
			{
				label: '2',
				name: 'quantity_destroyed',
				sort: 1,
				type: 'number'
			},
			{
				label: '3',
				name: 'remarks_party',
				sort: 1,
				type: 'string'
			},
			{
				label: '4',
				name: 'remarks_os',
				sort: 1,
				type: 'string'
			},
			{
				label: '5',
				name: 'validation'
			}
			],

			section_headers: [{
				label: 'Substances'
			},
			{
				label: 'Quantity destroyed'
			},
			{
				label: 'Remarks (party)'
			},
			{
				label: 'Remarks (Secretariat)'
			},
			{
				label: 'Status'
			}
			]
		},
		has_nonparty: {
			ordering_id: 0,
			status: null,
			saving: false,
			intro: '1. Fill in this form only if your country imported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide',
			title: 'Nonparty',
			name: 'has_nonparty',
			subtitle: 'in metric tonnes (not ODP tonnes)',
			description: 'Annexes A, B, C and E substances',
			isInvalid: false,

			fields_order: ['substance', 'blend', 'trade_party', 'quantity_import_new', 'quantity_import_recovered', 'quantity_export_new', 'quantity_export_recovered', 'remarks_party', 'remarks_os', 'validation'],
			modal_order: ['trade_party', 'quantity_import_new', 'quantity_import_recovered', 'quantity_export_new', 'quantity_export_recovered', 'validation'],
			blend_substance_headers: ['substance', 'percent', 'quantity_import_new', 'quantity_import_recovered', 'quantity_export_new', 'quantity_export_recovered'],
			form_fields: [],
			section_subheaders: [
				{
					label: '1',
					name: 'substance',
					sort: 1,
					type: 'string'
				},
				{
					label: '2',
					name: 'trade_party',
					sort: 1,
					type: 'string'
				},
				{
					label: 'New imports  <br> 3',
					name: 'quantity_import_new',
					sort: 1,
					type: 'number'
				},
				{
					label: 'Recovered and reclaimed imports <br> 4',
					name: 'quantity_import_recovered',
					sort: 1,
					type: 'number'
				},
				{
					label: 'New exports <br> 5',
					name: 'quantity_export_new',
					sort: 1,
					type: 'number'
				},
				{
					label: 'Recovered and reclaimed exports <br> 6',
					name: 'quantity_export_recovered',
					sort: 1,
					type: 'number'
				},
				{
					label: '7',
					name: 'remarks_party',
					sort: 1,
					type: 'string'
				},
				{
					label: '8',
					name: 'remarks_os',
					sort: 1,
					type: 'string'
				},
				{
					label: '9',
					name: 'validation'
				}
			],

			section_headers: [
				{
					label: 'Substances'
				},
				{
					label: 'Exporting party for quantities reported as imports <br> <b>OR</b> <br> Country of destination of exports'
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
					label: 'Remarks (party)'
				},
				{
					label: 'Remarks (Secretariat)'
				},
				{
					label: 'Status'
				}
			],

			comments: [{
				name: 'comments_party',
				selected: '',
				type: 'textarea',
				label: 'Party Comments'
			},
			{
				name: 'comments_secretariat',
				selected: '',
				type: 'textarea',
				label: 'Secretariat Comments'
			}
			]
		},

		has_emissions: {
			ordering_id: 0,
			status: null,
			saving: false,
			intro: '1. Fill in this form only if your country generated HFC 23 from any facility that produced (manufactured)  Annex C Group I or Annex F substances ',
			title: 'Emissions',
			name: 'has_emissions',
			subtitle: 'in metric tonnes (not ODP tonnes)',
			description: 'Annexes A, B, C and E substances',
			isInvalid: false,
			// used for identification when adding labels
			form_fields: [],

			fields_order: ['facility_name', 'quantity_generated', 'quantity_feedstock', 'quantity_destroyed', 'quantity_emitted', 'remarks_party', 'remarks_os', 'validation'],

			section_subheaders: [{
				label: '1',
				name: 'facility_name',
				sort: 1,
				type: 'string'
			},
			{
				label: '2',
				name: 'quantity_generated',
				sort: 1,
				type: 'number'
			},
			{
				label: '3',
				name: 'quantity_feedstock',
				sort: 1,
				type: 'number'
			},
			{
				label: '4',
				name: 'quantity_destroyed',
				sort: 1,
				type: 'number'
			},
			{
				label: '5',
				name: 'quantity_emitted',
				sort: 1,
				type: 'number'
			},
			{
				label: '6',
				name: 'remarks_party',
				sort: 1,
				type: 'string'
			},
			{
				label: '7',
				name: 'remarks_os',
				sort: 1,
				type: 'string'
			},
			{
				label: '8',
				name: 'validation'
			}
			],

			section_headers: [{
				label: 'Facility name or identifier',
				name: 'facility_name'
			},
			{
				label: 'Amount [Generated]* <br> (tonnes)',
				name: 'quantity_generated',
				tooltip: 'Amount [Generated] refers to amount that is captured, whether for destruction in another facility, feedstock or any other use. '
			},
			{
				label: 'Amount Used for Feedstock** <br> (tonnes)',
				name: 'quantity_feedstock',
				tooltip: 'Amount converted to other substances shall be treated as feedstock uses.'
			},
			{
				label: 'Amount Destroyed*** <br> (tonnes)',
				name: 'quantity_destroyed',
				tooltip: 'Amount Destroyed  refers to “Amount destroyed in the facility, with or without prior capture”'
			},
			{
				label: 'Amount of Emissions <br> (tonnes)',
				name: 'quantity_emitted'
			},
			{
				label: 'Remarks (party)',
				name: 'remarks_party'
			},
			{
				label: 'Remarks (Secretariat)',
				name: 'remarks_os'
			},
			{
				label: 'Status',
				name: 'validation'		
			}
			],
			comments: [{
				name: 'comments_party',
				selected: '',
				type: 'textarea',
				label: 'Party Comments'
			},
			{
				name: 'comments_secretariat',
				selected: '',
				type: 'textarea',
				label: 'Secretariat Comments'
			}
			]
		},
		attachments: []
	}
}
export default form
