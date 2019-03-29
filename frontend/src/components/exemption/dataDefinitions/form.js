import { getTabSubInfo } from '@/components/common/dataDefinitions/tabSubInfo'
import { setTabFiles } from '@/components/common/dataDefinitions/tabFiles'
import { getTabsCommonInfoForNominationAndApproved } from './tabsCommonInfoForNominationAndApproved'
import { getTabFlags } from '@/components/common/dataDefinitions/tabFlags'

const getFormExemption = ($gettext) => {
	const form = {
		formDetails: {
			tabsDisplay: ['sub_info', 'files', 'nomination', 'approved'],
			dataNeeded: [
				'initialData.countryOptions',
				'initialData.countryOptionsSubInfo',
				'initialData.substances',
				'current_submission',
				'initialData.display.substances',
				'initialData.display.countries',
				'initialData.submissionFormats',
				'currentUser',
				'permissions.form',
				'submissionDefaultValues.submission_format'
			],
			comments_default_properties: {
				exemption_nomination_remarks_secretariat: '',
				exemption_approved_remarks_secretariat: ''
			},
			comments_endpoint_url: 'submission_remarks'
		},
		tabs: {
			...setTabFiles($gettext),
			sub_info: {
				...getTabSubInfo($gettext)
			},
			nomination: {
				...getTabsCommonInfoForNominationAndApproved($gettext),
				name: 'nomination',
				formNumber: 1,
				status: null,
				title: $gettext('Nomination'),
				titleHtml: `<b>${$gettext('Nomination')}</b>`,
				endpoint_url: 'exemption_nomination_url',
				comments: {
					exemption_nomination_remarks_secretariat: {
						selected: '',
						type: 'textarea'
					}
				}
			},
			approved: {
				...getTabsCommonInfoForNominationAndApproved($gettext),
				name: 'approved',
				formNumber: 2,
				status: null,
				title: $gettext('Approved'),
				titleHtml: `<b>${$gettext('Approved')}</b>`,
				endpoint_url: 'exemption_approved_url',
				comments: {
					exemption_approved_remarks_secretariat: {
						selected: '',
						type: 'textarea'
					}
				}
			},
			flags: {
				...getTabFlags($gettext),
				form_fields: {
					flag_approved: {
						selected: false,
						type: 'checkbox',
						options: [
							{ text: $gettext('Approved'), value: true },
							{ text: $gettext('Not approved'), value: false }
						],
						radioType: 'stacked',
						disabled: true
					}
				},
				default_properties: {
					flag_approved: false
				}
			}
		}
	}
	return form
}

export {
	getFormExemption
}
