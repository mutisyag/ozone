import { intro_fields } from './questionnaire_fields'
import tab_sub_info from '@/components/common/dataDefinitions/tab_sub_info'
import tab_attachments from '@/components/common/dataDefinitions/tab_attachments'
import tab_flags from '@/components/common/dataDefinitions/tab_flags'

const form = {
	formDetails: {
		tabsDisplay: ['sub_info', 'questionaire_questions', 'has_imports', 'has_exports', 'has_produced', 'has_destroyed', 'has_nonparty', 'has_emissions', 'attachments', 'flags'],
		dataNeeded: [
			'initialData.countryOptions',
			'initialData.substances',
			'initialData.blends',
			'current_submission',
			'initialData.display.substances',
			'initialData.display.blends',
			'initialData.display.countries'
		]
	},
	tabs: {
		sub_info: {
			...tab_sub_info,
			detailsHtml: 'Respondents are requested to read the Introduction, the General Instructions, and the Definitions carefully before proceeding to the questionnaire and to refer to them as necessary when completing the data forms'
		},
		attachments: tab_attachments,
		questionaire_questions: {
			name: 'questionaire_questions',
			hasAssideMenu: false,
			endpoint_url: 'article7questionnaire_url',
			intro: 'Respondents are requested to read the Introduction in section 2, the General Instructions in section 4 and the Definitions in section 5 carefully before proceeding to the questionnaire and to refer to them as necessary when completing the data forms.',
			title: 'Questionnaire',
			titleHtml: '<b>Questionnaire</b>',
			detailsHtml: 'Respondents are requested to read the Introduction, the General Instructions, and the Definitions carefully before proceeding to the questionnaire and to refer to them as necessary when completing the data forms',
			status: null,
			isInvalid: false,
			description: '',
			form_fields: intro_fields,
			default_properties: {
				has_imports: false,
				has_exports: false,
				has_produced: false,
				has_destroyed: false,
				has_nonparty: false,
				has_emissions: false
			}
		},
		has_exports: {
			name: 'has_exports',
			hasAssideMenu: true,
			endpoint_url: 'article7exports_url',
			ordering_id: 0,
			validate: true,
			status: null,
			saving: false,
			formNumber: 2,
			intro: '1. Fill in this form only if your country imported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide',
			title: 'Exports',
			detailsHtml: 'Respondents are requested to read the Introduction, the General Instructions, and the Definitions carefully before proceeding to the questionnaire and to refer to them as necessary when completing the data forms',
			titleHtml: '<b>EXPORTS</b> <br> <small>Annexes A, B, C and E substances</small> <br> <small>in metric tonnes ( not ODP tonnes)</small>',
			tooltipForTitleHtml: 'Includes re exports. Ref. decisions IV/14 and XVII/16, paragraph 4.',
			subtitle: 'in metric tonnes (not ODP tonnes)',
			description: 'Annexes A, B, C and E substances',
			isInvalid: false,
			section_subheaders: [
				{
					label: '(1) <br> Group',
					name: 'group'
				},
				{
					label: '(2) <br> Substances',
					name: 'substance'
				},
				{
					label: '(3) <br> Country of destination of exports',
					name: 'destination_party'
				},
				{
					label: '(4) <br> New',
					name: 'quantity_total_new'
				},
				{
					label: '(5) <br> Recovered and reclaimed',
					name: 'quantity_total_recovered'
				},
				{
					label: '(6) <br> Quantity of new substances exported as feedstock',
					name: 'quantity_feedstock'
				},
				{
					label: '(7) <br> Quantity',
					name: 'quantity_exempted'
				},
				{
					label: ' (8) <br> Decision / type of use or remark',
					name: 'decision_exempted'
				},
				{
					label: '(9) <br> Status',
					name: 'validation'
				}
			],

			section_headers: [{
				label: ''
			},
			{
				label: ''
			},
			{
				label: '',
				tooltip: 'Applicable to all substances, including those contained in mixtures and blends.'
			},
			{
				label: 'Total Quantity Exported for All Uses',
				colspan: 2
			},
			{
				label: '',
				tooltip: 'Do not deduct from total production in column 3 of data form 3 (data on production).'
			},
			{
				label: 'Quantity of new substance exported for exempted essential, critical, high-ambient-temperature or other uses',
				colspan: 2,
				tooltip: 'Against each substance exported for exempted essential, critical, high-ambient-temperature or other uses, please specify the Meeting of the Parties decision that approved the use. Should the column space be insufficient, further information can be provided in the “comments” box above.'
			},
			{
				label: ''
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
				type: 'textarea'
			},
			{
				name: 'comments_secretariat',
				selected: '',
				type: 'textarea'
			}
			],
			footnotes: ['[1] Tonne = Metric ton.'],
			default_properties: {
				remarks_party: '',
				remarks_os: '',
				quantity_total_new: null,
				quantity_total_recovered: null,
				quantity_feedstock: null,
				quantity_critical_uses: null,
				decision_critical_uses: '',
				quantity_essential_uses: null,
				decision_essential_uses: '',
				quantity_high_ambient_temperature: null,
				decision_high_ambient_temperature: '',
				quantity_laboratory_analytical_uses: null,
				decision_laboratory_analytical_uses: '',
				quantity_process_agent_uses: null,
				decision_process_agent_uses: '',
				quantity_quarantine_pre_shipment: null,
				decision_quarantine_pre_shipment: '',
				destination_party: null,
				substance: null,
				blend: null,
				decision: null
			}
		},
		has_imports: {
			name: 'has_imports',
			hasAssideMenu: true,
			endpoint_url: 'article7imports_url',
			ordering_id: 0,
			status: null,
			validate: true,
			saving: false,
			formNumber: 1,
			intro: '1. Fill in this form only if your country imported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide',
			title: 'Imports',
			titleHtml: '<b>IMPORTS</b> <br> <small>Annexes A, B, C and E substances</small> <br> <small>in metric tonnes ( not ODP tonnes)</small>',
			detailsHtml: 'Fill in this form only if your country imported CFCs, halons, carbon tetrachloride, methyl chloroform, HCFCs, HBFCs, bromochloromethane, methyl bromide or HFCs',
			comments: [{
				name: 'comments_party',
				selected: '',
				type: 'textarea'
			},
			{
				name: 'comments_secretariat',
				selected: '',
				type: 'textarea'
			}
			],
			subtitle: 'in metric tonnes (not ODP tonnes)',
			description: 'Annexes A, B, C and E substances',
			blend_substance_headers: ['substance', 'percent', 'quantity_total_new', 'quantity_total_recovered', 'quantity_feedstock', 'quantity_exempted'],
			section_subheaders: [{
				name: 'group',
				label: '(1) Group'
			},
			{
				name: 'substance',
				label: '(2) Substance'
			},
			{
				name: 'source_party',
				label: '(3) <br> Exporting party for quantities reported as imports'
			},
			{
				label: '(4) <br> New',
				name: 'quantity_total_new'
			},
			{
				label: '(5) <br> Recovered and reclaimed',
				name: 'quantity_total_recovered'
			},
			{
				name: 'quantity_feedstock',
				label: '(6) <br> Quantity of new substances imported as feedstock'
			},
			{
				label: '(7) <br> Quantity',
				name: 'quantity_exempted'
			},
			{
				label: '(8) <br> Decision / type of use or remark',
				name: 'decision_exempted'
			},
			{
				label: '(9) <br> Status',
				name: 'validation'
			}
			],

			section_headers: [{
				label: ''
			},
			{
				label: ''
			},
			{
				label: '',
				tooltip: 'Applicable to all substances, including those contained in mixtures and blends.'
			},
			{
				label: 'Total Quantity Imported for All Uses',
				colspan: 2
			},
			{
				label: '',
				tooltip: 'Do not deduct from total production in column 3 of data form 3 (data on production).'
			},
			{
				label: 'Quantity of new substance imported for exempted essential, critical, high-ambient-temperature or other uses',
				colspan: 2,
				tooltip: 'Against each substance imported for exempted essential, critical, high-ambient-temperature or other uses, please specify the Meeting of the Parties decision that approved the use. Should the column space be insufficient, further information can be provided in the “comments” box above.'
			},
			{
				label: ''
			}
			],
			fields_order: ['substance', 'blend', 'source_party', 'quantity_total_new', 'quantity_total_recovered', 'quantity_feedstock', 'quantity_exempted', 'decision_exempted', 'validation'],
			hidden_fields_order: ['quantity_essential_uses', 'decision_essential_uses', 'quantity_critical_uses', 'decision_critical_uses', 'quantity_high_ambient_temperature', 'decision_high_ambient_temperature', 'quantity_process_agent_uses', 'decision_process_agent_uses', 'quantity_laboratory_analytical_uses', 'decision_laboratory_analytical_uses', 'quantity_quarantine_pre_shipment', 'decision_quarantine_pre_shipment', 'quantity_other_uses', 'decision_other_uses'],
			modal_order: ['source_party', 'quantity_total_new', 'quantity_total_recovered', 'quantity_feedstock'],
			form_fields: [],
			isInvalid: false,
			footnotes: ['[1] Tonne = Metric ton.'],
			default_properties: {
				remarks_party: '',
				remarks_os: '',
				quantity_total_new: null,
				quantity_total_recovered: null,
				quantity_feedstock: null,
				quantity_critical_uses: null,
				decision_critical_uses: '',
				quantity_essential_uses: null,
				decision_essential_uses: '',
				quantity_high_ambient_temperature: null,
				decision_high_ambient_temperature: '',
				quantity_laboratory_analytical_uses: null,
				decision_laboratory_analytical_uses: '',
				quantity_process_agent_uses: null,
				decision_process_agent_uses: '',
				quantity_quarantine_pre_shipment: null,
				decision_quarantine_pre_shipment: '',
				source_party: null,
				substance: null,
				blend: null,
				decision: null
			}
		},
		has_produced: {
			name: 'has_produced',
			hasAssideMenu: true,
			endpoint_url: 'article7productions_url',
			ordering_id: 0,
			status: null,
			validate: true,
			saving: false,
			formNumber: 3,
			intro: '1. Fill in this form only if your country imported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide',
			title: 'Production',
			titleHtml: '<b>PRODUCTION </b> <br><small> in tonnes (not ODP or GWP tonnes)<br>Annex A, B, C, E and F substances  </small>',
			detailsHtml: 'Fill in this form only if your country produced CFCs, halons, carbon tetrachloride, methyl chloroform, HCFCs, HBFCs, bromochloromethane, methyl bromide or HFCs',
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
					name: 'group',
					label: '(1) <br> Group'
				},
				{
					label: '(2) <br> Substance',
					name: 'substance'
				},
				{
					label: '(3) <br> Total production for all uses',
					name: 'quantity_total_produced'
				},
				{
					label: '(4) <br> Production for feedstock uses within your country',
					name: 'quantity_feedstock'
				},
				{
					label: '(5) <br> Quantity',
					name: 'quantity_exempted'
				},
				{
					label: '(6) <br> Decision / type of use',
					name: 'decision_exempted'
				},
				{
					label: '(7) <br> Production for supply to Article 5 countries in accordance with Articles 2A 2H and 5',
					name: 'quantity_article_5'
				},
				{
					label: '(8) <br> Status',
					name: 'validation'
				}
			],

			section_headers: [
				{
					label: ''
				},
				{
					label: ''
				},
				{
					label: ''
				},
				{
					label: ''
				},
				{
					label: 'Production for exempted essential, critical or other uses within your country',
					colspan: 2,
					tooltip: 'Against each substance produced for exempted essential, critical or other uses, please specify the Meeting of the Parties decision that approved the use. Should the column space be insufficient, further information can be provided in the “comments” box above.'
				},
				{
					label: ''
				},
				{
					label: ''
				}
			],

			special_headers: {

				section_headers: [
					{
						label: ''
					},
					{
						label: ''
					},
					{
						label: ''
					},
					{
						label: 'Production for feedstock uses within your country',
						colspan: 2
					},
					{
						label: 'Production for exempted essential, critical or other uses within your country',
						colspan: 2,
						tooltip: 'Against each substance produced for exempted essential, critical or other uses, please specify the Meeting of the Parties decision that approved the use. Should the column space be insufficient, further information can be provided in the “comments” box above.'
					},
					{
						label: ''
					},
					{
						label: ''
					}
				],

				section_subheaders: [
					{
						name: 'group',
						label: '(1) <br> Group'
					},
					{
						label: '(2) <br> Substance',
						name: 'substances'
					},
					{
						label: '(3) <br> Captured for all uses',
						name: 'quantity_total_produced'
					},
					{
						label: '(4a) <br> Captured for feedstock uses within your country',
						name: 'quantity_feedstock'
					},
					{
						label: '(4b) <br> Captured for destruction',
						name: 'quantity_for_destruction'
					},
					{
						label: '(5) <br> Quantity',
						name: 'quantity_exempted'
					},
					{
						label: '(6) <br> Decision / type of use',
						name: 'decision_exempted'
					},
					{
						label: '(7) <br> Production for supply to Article 5 countries in accordance with Articles 2A 2H and 5',
						name: 'quantity_article_5'
					},
					{
						label: '(8) <br> Status',
						name: 'validation'
					}
				]
			},

			comments: [{
				name: 'comments_party',
				selected: '',
				type: 'textarea'
			},
			{
				name: 'comments_secretariat',
				selected: '',
				type: 'textarea'
			}
			],
			default_properties: {
				remarks_party: '',
				remarks_os: '',
				quantity_critical_uses: null,
				decision_critical_uses: '',
				quantity_essential_uses: null,
				decision_essential_uses: '',
				quantity_high_ambient_temperature: null,
				decision_high_ambient_temperature: '',
				quantity_laboratory_analytical_uses: null,
				decision_laboratory_analytical_uses: '',
				quantity_process_agent_uses: null,
				decision_process_agent_uses: '',
				quantity_quarantine_pre_shipment: null,
				decision_quarantine_pre_shipment: '',
				quantity_total_produced: null,
				quantity_feedstock: null,
				quantity_article_5: null,
				substance: null
			}
		},
		has_destroyed: {
			name: 'has_destroyed',
			hasAssideMenu: true,
			endpoint_url: 'article7destructions_url',
			ordering_id: 0,
			status: null,
			validate: true,
			saving: false,
			formNumber: 4,
			intro: '1. Fill in this form only if your country imported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide',
			title: 'Destruction',
			titleHtml: '<b>QUANTITY OF SUBSTANCES DESTROYED </b> <br><small> in tonnes (not ODP or GWP tonnes)<br>Annex A, B, C, E and F substances  </small>',
			detailsHtml: 'Fill in this form only if your country destroyed CFCs, halons, carbon tetrachloride, methyl chloroform, HCFCs, HBFCs, bromochloromethane, methyl bromide or HFCs',
			subtitle: 'in metric tonnes (not ODP tonnes)',
			description: 'Annexes A, B, C and E substances',
			fields_order: ['substance', 'quantity_destroyed', 'remarks_party', 'remarks_os', 'validation'],
			blend_substance_headers: ['substance', 'percent', 'quantity_destroyed'],
			modal_order: ['quantity_destroyed'],
			isInvalid: false,
			form_fields: [],
			section_subheaders: [{
				label: '(1) Group',
				name: 'group'
			},
			{
				label: '(2) Substance',
				name: 'substance'
			},
			{
				label: '(3) Quantity destroyed',
				name: 'quantity_destroyed'
			},
			{
				label: '(4) Remarks (party)',
				name: 'remarks_party'
			},
			{
				label: '(5) Remarks (secretariat)',
				name: 'remarks_os'
			},
			{
				label: '(6) Status',
				name: 'validation'
			}
			],

			section_headers: [{
				label: ''
			},
			{
				label: ''
			},
			{
				label: ''
			},
			{
				label: ''
			},
			{
				label: ''
			}
			],
			default_properties: {
				remarks_party: '',
				remarks_os: '',
				quantity_destroyed: null,
				substance: null,
				blend: null
			}
		},
		has_nonparty: {
			name: 'has_nonparty',
			hasAssideMenu: true,
			endpoint_url: 'article7nonpartytrades_url',
			ordering_id: 0,
			status: null,
			validate: true,
			saving: false,
			formNumber: 5,
			intro: '1. Fill in this form only if your country imported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide',
			title: 'Nonparty',
			titleHtml: '<b>IMPORTS FROM AND/OR EXPORTS TO NON PARTIES </b> <br><small> in tonnes (not ODP or GWP tonnes)<br>Annex A, B, C and E substances  </small>',
			tooltipForTitleHtml: 'See definition of “non parties” in Instruction V.',
			detailsHtml: 'Fill in this form only if your country imported or exported CFCs, halons, carbon tetrachloride, methyl chloroform, HCFCs, HBFCs, bromochloromethane or methyl bromide to non parties ',
			subtitle: 'in metric tonnes (not ODP tonnes)',
			description: 'Annexes A, B, C and E substances',
			isInvalid: false,
			fields_order: ['substance', 'blend', 'trade_party', 'quantity_import_new', 'quantity_import_recovered', 'quantity_export_new', 'quantity_export_recovered', 'remarks_party', 'remarks_os', 'validation'],
			modal_order: ['trade_party', 'quantity_import_new', 'quantity_import_recovered', 'quantity_export_new', 'quantity_export_recovered', 'validation'],
			blend_substance_headers: ['substance', 'percent', 'quantity_import_new', 'quantity_import_recovered', 'quantity_export_new', 'quantity_export_recovered'],
			form_fields: [],
			section_subheaders: [{
				label: '(1) <br> Group',
				name: 'group'
			},
			{
				label: '(2) <br> Substance',
				name: 'substance'
			},
			{
				label: '(3) <br> Exporting party for quantities reported as imports <br> <b>OR</b> <br> Country of destination of exports',
				name: 'trade_party'
			},
			{
				label: '(4) <br> New imports',
				name: 'quantity_import_new'
			},
			{
				label: '(5) <br> Recovered and reclaimed imports',
				name: 'quantity_import_recovered'
			},
			{
				label: '(6) <br> New exports',
				name: 'quantity_export_new'
			},
			{
				label: '(7) <br> Recovered and reclaimed exports',
				name: 'quantity_export_recovered'
			},
			{
				label: '(8) <br> Remarks (party)',
				name: 'remarks_party'
			},
			{
				label: '(9) <br> Remarks (Secretariat)',
				name: 'remarks_os'
			},
			{
				label: 'Status <br> (10)',
				name: 'validation'
			}
			],

			section_headers: [
				{
					label: ''
				},
				{
					label: ''
				},
				{
					label: ''
				},
				{
					label: 'Quantity of imports from non-parties',
					colspan: 2,
					tooltip: 'See definition of “non parties” in Instruction V.'
				},
				{
					label: 'Quantity of exports to non-parties',
					colspan: 2,
					tooltip: 'See definition of “non parties” in Instruction V.'
				},
				{
					label: ''
				},
				{
					label: ''
				},
				{
					label: ''
				}
			],

			comments: [{
				name: 'comments_party',
				selected: '',
				type: 'textarea'
			},
			{
				name: 'comments_secretariat',
				selected: '',
				type: 'textarea'
			}
			],
			default_properties: {
				remarks_party: '',
				remarks_os: '',
				quantity_import_new: null,
				quantity_import_recovered: null,
				quantity_export_new: null,
				quantity_export_recovered: null,
				substance: null,
				blend: null,
				trade_party: null
			}
		},
		has_emissions: {
			name: 'has_emissions',
			hasAssideMenu: false,
			endpoint_url: 'article7emissions_url',
			ordering_id: 0,
			status: null,
			validate: true,
			saving: false,
			formNumber: 6,
			title: 'Emissions',
			titleHtml: '<b>DATA ON QUANTITY OF EMISSIONS OF HFC 23 FROM FACILITIES MANUFACTURING ANNEX C GROUP I OR ANNEX F SUBSTANCES</b><br><small>In metric tons, not ODP or CO2-equivalent tonnes.</small>',
			tooltipHtml: 'Information in columns 2 to 5 is excluded from the reporting requirements under Article 7 of the Protocol and is provided on a voluntary basis',
			detailsHtml: 'Fill in this form only if your country generated HFC 23 from any facility that produced (manufactured) Annex C Group I or Annex F substances ',
			subtitle: 'in metric tonnes (not ODP tonnes)',
			description: 'Annexes A, B, C and E substances',
			isInvalid: false,
			// used for identification when adding labels
			form_fields: [],
			get fields_order() {
				return this.section_subheaders.map(x => x.name)
			},
			section_subheaders: [{
				label: '(1) <br> Facility name or identifier',
				name: 'facility_name'
			},
			{
				label: '(2) <br> Total amount generated',
				name: 'quantity_generated'
			},
			{
				label: '(3a) <br> For all uses',
				name: 'quantity_captured_all_uses'
			},
			{
				label: '(3b) <br> For feedstock use in your country',
				name: 'quantity_captured_feedstock'
			},
			{
				label: '(3c) <br> For Destruction',
				name: 'quantity_captured_for_destruction'
			},
			{
				label: '(4) <br> Amount used for feedstock without prior capture',
				name: 'quantity_feedstock'
			},
			{
				label: '(5) <br> Amount destroyed without prior capture',
				name: 'quantity_destroyed'
			},
			{
				label: '(6) <br> Amount of generated emissions',
				name: 'quantity_emitted'
			},
			{
				label: '(7) <br> Remarks (party)',
				name: 'remarks_party'
			},
			{
				label: '(8) Remarks (secretariat)',
				name: 'remarks_os'
			},
			{
				label: '(9) Status',
				name: 'validation'
			}
			],

			section_headers: [{
				label: ''
			},
			{
				label: '',
				tooltip: 'Refers to the total amount whether captured or not. The sum of these amounts is not to be reported under data form 3'
			},
			{
				label: '(3) Amout generated and captured',
				tooltip: 'Refers to the total amount whether captured or not. The sum of these amounts is not to be reported under data form 3',
				colspan: 3
			},
			{
				label: '',
				tooltip: 'Amount converted to other substances in the facility. The sum of these amounts is not to be reported under data form 3'
			},
			{
				label: '',
				tooltip: 'Amount destroyed in the facility'
			},
			{
				label: ''
			},
			{
				label: ''
			},
			{
				label: ''
			},
			{
				label: ''
			}
			],
			comments: [{
				name: 'comments_party',
				selected: '',
				type: 'textarea'
			},
			{
				name: 'comments_secretariat',
				selected: '',
				type: 'textarea'
			}
			],
			default_properties: {
				remarks_party: '',
				remarks_os: '',
				ordering_id: null,
				facility_name: '',
				quantity_generated: null,
				quantity_captured_all_uses: null,
				quantity_captured_feedstock: null,
				quantity_captured_for_destruction: null,
				quantity_feedstock: null,
				quantity_destroyed: null,
				quantity_emitted: null
			}
		},
		flags: tab_flags
	}
}
export default form
