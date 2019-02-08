import { getTabSubInfo } from '@/components/common/dataDefinitions/tabSubInfo'
import { getTabFiles } from '@/components/common/dataDefinitions/tabFiles'
import { getTabsCommonInfoForNominationAndApproved } from './tabsCommonInfoForNominationAndApproved'

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
				hideInfoButton: true,
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
				...getTabsCommonInfoForNominationAndApproved($gettext),
				name: 'nomination',
				formNumber: 1,
				title: $gettext('Nomination'),
				titleHtml: `<b>${$gettext('Nomination')}</b>`,
				endpoint_url: 'exemption_nomination_url'
			},
			approved: {
				...getTabsCommonInfoForNominationAndApproved($gettext),
				name: 'approved',
				formNumber: 2,
				title: $gettext('Approved'),
				titleHtml: `<b>${$gettext('Approved')}</b>`,
				endpoint_url: 'exemption_approved_url'
			}
		}
	}
	return form
}

export {
	getFormExemption
}
