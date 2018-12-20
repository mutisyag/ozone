import tab_sub_info from '@/components/common/dataDefinitions/tab_sub_info'
import tab_attachments from '@/components/common/dataDefinitions/tab_attachments'
import tab_flags from '@/components/common/dataDefinitions/tab_flags'

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
			title: 'Imports',
			titleHtml: '<b>Consumption (imports)</b> <br><small>Annex F substances for exempted subsectors, \n in metric tonnes (not ODP or CO2-equivalent tonnes)</small>',
			detailsHtml: '1. Fill in this form only if your country is listed in appendix II to decision XXVIII/2, has formally notified the Secretariat of its intention to use the high-ambient-temperature exemption, and produced HFCs for its own use in the subsectors contained in appendix I to decision XXVIII/2',
			isInvalid: false,
			form_fields: [],
			special_fields_order: [],
			hidden_fields_order: [],
			blend_substance_headers: ['substance', 'percent', 'quantity_total_produced', 'quantity_feedstock', 'quantity_exempted', 'quantity_article_5'],
			get fields_order() {
				return this.section_subheaders.map(x => x.name)
			},
			get input_fields() {
				return this.section_subheaders.filter(x => x.isInput).map(x => x.name)
			},
			get modal_order() {
				return this.input_fields
			},
			section_subheaders: [{
				label: '(1)<br>Annex/group',
				name: 'group',
				sort: 1,
				colspan: 2,
				type: 'string'
			}, {
				label: '(2)<br>Substance',
				name: 'substance',
				sort: 1,
				colspan: 2,
				type: 'string'
			}, {
				label: '(3)<br>New imports for use in multi-split air conditioners',
				name: 'prop1',
				isInput: true
			}, {
				label: '(4)<br>New imports for use in split ducted air conditioners',
				name: 'prop2',
				isInput: true
			}, {
				label: '(5)<br>New imports for use in ducted commercial packaged (self-contained) air conditioners',
				name: 'prop3',
				isInput: true
			}, {
				label: '(6)',
				name: 'validation'
			}
			],

			section_headers: [{
				label: ''
			}, {
				label: ''
			}, {
				label: 'Quantity of new substances imported for approved subsectors to which the high-ambient-temperature exemption applies*',
				colspan: 3,
				tooltip: 'Only bulk gases for servicing of exempted equipment should be reported here, not gases imported inside pre-charged equipment.'
			}, {
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
			],
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
			title: 'Production',
			titleHtml: '<b>PRODUCTION </b> <br><small> Annex F substances for exempted subsectors, <br>in metric tonnes (not ODP or CO2-equivalent tonnes)  </small>',
			detailsHtml: '1. Fill in this form only if your country is listed in appendix II to decision XXVIII/2, has formally notified the Secretariat of its intention to use the high-ambient-temperature exemption, and produced HFCs for its own use in the subsectors contained in appendix I to decision XXVIII/2',
			isInvalid: false,
			form_fields: [],
			blend_substance_headers: ['substance', 'percent', 'quantity_total_produced', 'quantity_feedstock', 'quantity_exempted', 'quantity_article_5'],
			get fields_order() {
				return this.section_subheaders.map(x => x.name)
			},
			get input_fields() {
				return this.section_subheaders.filter(x => x.isInput).map(x => x.name)
			},
			get modal_order() {
				return this.input_fields
			},
			section_subheaders: [{
				label: '(1)<br>Annex/group',
				name: 'group',
				colspan: 2
			}, {
				label: '(2)<br>Substance',
				name: 'substance',
				colspan: 2
			}, {
				label: '(3)<br>New production for use in multi-split air conditioners',
				name: 'prop1',
				isInput: true
			}, {
				label: '(4)<br>New production for use in split ducted air conditioners',
				name: 'prop2',
				isInput: true
			}, {
				label: '(5)<br>New production for use in ducted commercial packaged (self-contained) air conditioners',
				name: 'prop3',
				isInput: true
			}, {
				label: '(6)',
				name: 'validation'
			}],

			section_headers: [{
				label: ''
			}, {
				label: ''
			}, {
				label: 'Quantity of new substances produced for approved subsectors to which the high-ambient-temperature exemption applies (production should be for use within the producing country*',
				colspan: 3,
				tooltip: 'For each substance produced for use in subsectors that may be approved after the assessments under paragraphs 32 and 33 of decision XXVIII/2, please specify the approved subsector. Should the column space be insufficient, further information can be provided in the “comments” box above.'
			}, {
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
		flags: tab_flags
	}
}
export default form
