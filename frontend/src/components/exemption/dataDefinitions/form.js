import { getTabSubInfo } from '@/components/common/dataDefinitions/tabSubInfo'
import { setTabFiles } from '@/components/common/dataDefinitions/tabFiles'
import { getTabsCommonInfoForNominationAndApproved } from './tabsCommonInfoForNominationAndApproved'

const getFormExemption = ($gettext) => {
	const tabSubInfo = getTabSubInfo($gettext)
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
				'currentUser',
				'permissions.form'
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
			}
		}
	}
	return form
}

export {
	getFormExemption
}
