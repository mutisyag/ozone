import tab_sub_info from '@/components/common/dataDefinitions/tab_sub_info'
import tab_attachments from '@/components/common/dataDefinitions/tab_attachments'

const form = {
	formDetails: {
		tabsDisplay: ['sub_info', 'has_imports', 'has_produced', 'attachments'],
		dataNeeded: [
			'initialData.countryOptions',
			'initialData.substances',
			'initialData.blends'
		]
	},
	tabs: {
		sub_info: tab_sub_info,
		attachments: tab_attachments,
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
			formNumber: 2,
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
		}
	}
}
export default form
