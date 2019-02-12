import { getTabSubInfo } from '@/components/common/dataDefinitions/tabSubInfo'
import { getTabFiles } from '@/components/common/dataDefinitions/tabFiles'
import { getTabFlags } from '@/components/common/dataDefinitions/tabFlags'

const getFormRaf = ($gettext) => {
	const form = {
		formDetails: {
			tabsDisplay: ['sub_info', 'essencrit', 'files'],
			dataNeeded: [
				'initialData.countryOptions',
				'initialData.substances',
				'initialData.blends',
				'current_submission',
				'initialData.display.substances',
				'initialData.display.blends',
				'initialData.display.countries',
				'currentUser',
				'permissions.form'
			],
			comments_default_properties: {
				'hat_imports_remarks_party': '',
				'hat_imports_remarks_secretariat': '',
				'hat_production_remarks_party': '',
				'hat_production_remarks_secretariat': ''
			},
			comments_endpoint_url: 'submission_remarks'
		},
		tabs: {
			sub_info: {
				...getTabSubInfo($gettext),
				hideInfoButton: true,
				detailsHtml: $gettext('Respondents are requested to read the Introduction, the General Instructions, and the Definitions carefully before proceeding to the questionnaire and to refer to them as necessary when completing the data forms')
			},
			files: {
				...getTabFiles($gettext),
				hideInfoButton: true
			},
			essencrit: {
				name: 'essencrit',
				hasAssideMenu: true,
				endpoint_url: 'raf_url',
				ordering_id: 0,
				status: null,
				validate: true,
				saving: false,
				formNumber: 2,
				title: $gettext('Essential and critical uses'),
				titleHtml: `<b>${$gettext('PRODUCTION')}</b><br><small>${$gettext('Annex F substances for exempted subsectors')}<br>${$gettext('in metric tonnes (not ODP or CO2-equivalent tonnes)')}</small>`,
				detailsHtml: `1. ${$gettext('Fill in this form only if your country is listed in appendix II to decision XXVIII/2, has formally notified the Secretariat of its intention to use the high-ambient-temperature exemption, and produced HFCs for its own use in the subsectors contained in appendix I to decision XXVIII/2')}`,
				isInvalid: false,
				form_fields: [],
				blend_substance_headers: ['substance', 'percent', 'quantity_msac', 'quantity_sdac', 'quantity_dcpac'],
				get fields_order() {
					return this.section_subheaders.map(x => x.name)
				},
				get input_fields() {
					return this.section_subheaders.filter(x => x.isInput).map(x => x.name)
				},
				section_subheaders: [{
					label: `(1)<br>${$gettext('Annex/group')}`,
					name: 'group',
					colspan: 2
				}, {
					label: `(2)<br>${$gettext('Ozone depletig substances')}`,
					name: 'substance',
					colspan: 2
				}, {
					label: `(3)<br>${$gettext('Amount exempted')}`,
					name: 'quantity_exempted',
					isInput: true
				}, {
					label: `(4)<br>${$gettext('Amount acquired by production')}`,
					name: 'quantity_production',
					isInput: true
				}, {
					label: `(5)<br>${$gettext('Amount acquired by import & countries of manufacture')}`,
					name: 'quantity_import'
				}, {
					label: `(6)<br>${$gettext('Total acquired')}`,
					name: 'quantity_acquired'
				}, {
					label: `(7)<br>${$gettext('Authorized but not acquired')}`,
					name: 'quantity_authorized_not_acquired'
				}, {
					label: `(8)<br>${$gettext('On hand start of the year')}`,
					name: 'on_hand_start_year',
					isInput: true
				}, {
					label: `(9)<br>${$gettext('Available for use')}`,
					name: 'available_for_use',
					isInput: true
				}, {
					label: `(10)<br>${$gettext('Used')}`,
					name: 'quantity_used',
					isInput: true
				}, {
					label: `(11)<br>${$gettext('Amount exported')}`,
					name: 'quantity_exported',
					isInput: true
				}, {
					label: `(12)<br>${$gettext('Amount destroyed')}`,
					name: 'quantity_destroyed',
					isInput: true
				}, {
					label: `(13)<br>${$gettext('On hand end of year')}`,
					name: 'on_hand_end_year'
				}, {
					label: `(16)<br>${$gettext('Status')}`,
					name: 'validation'
				}],

				section_headers: [{
					label: '',
					colspan: 16
				}
				],
				comments: {
					hat_production_remarks_party: {
						name: 'hat_production_remarks_party',
						selected: '',
						type: 'textarea'
					},
					hat_production_remarks_secretariat: {
						name: 'hat_production_remarks_secretariat',
						selected: '',
						type: 'textarea'
					}
				},
				default_properties: {
					'imports': [],
					'remarks_party': '',
					'remarks_os': '',
					'ordering_id': null,
					'quantity_exempted': null,
					'quantity_production': null,
					'quantity_used': null,
					'quantity_exported': null,
					'quantity_destroyed': null,
					'on_hand_start_year': null,
					'substance': null
				}
			},
			flags: getTabFlags($gettext)
		}
	}
	return form
}

export {
	getFormRaf
}
