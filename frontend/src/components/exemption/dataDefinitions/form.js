import { getTabSubInfo } from '@/components/common/dataDefinitions/tabSubInfo'
import { getTabFiles } from '@/components/common/dataDefinitions/tabFiles'

const getFormExemption = ($gettext) => {
	const tabSubInfo = getTabSubInfo($gettext)
	const form = {
		formDetails: {
			tabsDisplay: ['sub_info', 'files', 'nomination', 'approved'],
			dataNeeded: [
				'initialData.countryOptions',
				'initialData.substances',
				'current_submission',
				'initialData.display.substances',
				'initialData.display.countries',
				'currentUser',
				'permissions.form'
			]
		},
		tabs: {
			sub_info: {
				...tabSubInfo,
				fields_order: [...tabSubInfo.fields_order],
				form_fields: {
					...tabSubInfo.form_fields
				},
				default_properties: {
					...tabSubInfo.default_properties
				}
			},
			files: getTabFiles($gettext),
			nomination: {
				name: 'nomination',
				hasAssideMenu: true,
				endpoint_url: 'exemptionnomination_url',
				title: $gettext('Nomination'),
				default_properties: {},
				form_fields: [],
				section_subheaders: []
			},
			approved: {
				name: 'approved',
				hasAssideMenu: true,
				endpoint_url: 'exemptionapproved_url',
				ordering_id: 0,
				validate: true,
				status: null,
				saving: false,
				formNumber: 2,
				intro: `1. ${$gettext('Fill in this form only if your country imported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide')}`,
				title: $gettext('Approved'),
				detailsHtml: $gettext('Respondents are requested to read the Introduction, the General Instructions, and the Definitions carefully before proceeding to the questionnaire and to refer to them as necessary when completing the data forms'),
				titleHtml: `<b>${$gettext('Approved')}</b> <br> <small>${$gettext('Annexes A, B, C and E substances')}</small> <br> <small>${$gettext('in metric tonnes (not ODP tonnes)')}</small>`,
				tooltipForTitleHtml: $gettext('Includes re exports. Ref. decisions IV/14 and XVII/16, paragraph 4.'),
				subtitle: $gettext('in metric tonnes (not ODP tonnes)'),
				description: $gettext('Annexes A, B, C and E substances'),
				isInvalid: false,
				section_subheaders: [
					{
						label: `(1) <br> ${$gettext('Group')}`,
						name: 'group'
					},
					{
						label: `(2) <br> ${$gettext('Substances')}`,
						name: 'substance'
					},
					{
						label: `(3) <br> ${$gettext('Country of destination of exports')}`,
						name: 'destination_party'
					},
					{
						label: `(4) <br> ${$gettext('New')}`,
						name: 'quantity_total_new'
					},
					{
						label: `(5) <br> ${$gettext('Recovered and reclaimed')}`,
						name: 'quantity_total_recovered'
					},
					{
						label: `(6) <br> ${$gettext('Quantity of new substances exported as feedstock')}`,
						name: 'quantity_feedstock'
					},
					{
						label: `(7) <br> ${$gettext('Quantity')}`,
						name: 'quantity_exempted'
					},
					{
						label: `(8) <br> ${$gettext('Decision / type of use or remark')}`,
						name: 'decision_exempted'
					},
					{
						label: `(9) <br> ${$gettext('Status')}`,
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
					tooltip: $gettext('Applicable to all substances, including those contained in mixtures and blends.')
				},
				{
					label: $gettext('Total Quantity Exported for All Uses'),
					colspan: 2
				},
				{
					label: '',
					tooltip: $gettext('Do not deduct from total production in column 3 of data form 3 (data on production).')
				},
				{
					label: $gettext('Quantity of new substance exported for exempted essential, critical, high-ambient-temperature or other uses'),
					colspan: 2,
					tooltip: $gettext('Against each substance exported for exempted essential, critical, high-ambient-temperature or other uses, please specify the Meeting of the Parties decision that approved the use. Should the column space be insufficient, further information can be provided in the “comments” box above.')
				},
				{
					label: ''
				}
				],

				blend_substance_headers: ['substance', 'percent', 'quantity_total_new', 'quantity_total_recovered', 'quantity_feedstock', 'quantity_exempted'],

				fields_order: ['substance', 'blend', 'destination_party', 'quantity_total_new', 'quantity_total_recovered', 'quantity_feedstock', 'quantity_exempted', 'decision_exempted', 'validation'],
				hidden_fields_order: ['quantity_quarantine_pre_shipment', 'decision_quarantine_pre_shipment', 'quantity_essential_uses', 'decision_essential_uses', 'quantity_critical_uses', 'decision_critical_uses', 'quantity_high_ambient_temperature', 'decision_high_ambient_temperature', 'quantity_laboratory_analytical_uses', 'decision_laboratory_analytical_uses', 'quantity_process_agent_uses', 'decision_process_agent_uses', 'quantity_other_uses', 'decision_other_uses', 'quantity_polyols', 'decision_polyols'],
				modal_order: ['destination_party', 'quantity_total_new', 'quantity_total_recovered', 'quantity_feedstock'],
				form_fields: [],

				comments: {
					exports_remarks_party: {
						selected: '',
						type: 'textarea'
					},
					exports_remarks_secretariat: {
						selected: '',
						type: 'textarea'
					}
				},
				footnotes: [`[1] ${$gettext('Tonne = Metric ton.')}`],
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
					quantity_polyols: null,
					decision_polyols: null,
					substance: null,
					decision: null
				}
			}
		}
	}
	return form
}

export {
	getFormExemption
}
