import { getTabSubInfo } from '@/components/common/dataDefinitions/tabSubInfo'
import { getTabFiles } from '@/components/common/dataDefinitions/tabFiles'
import { getObjectLevel1PropertyValuesAsArray } from '@/components/common/services/utilsService'
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
			],
			comments_default_properties: {
				exemption_nomination_remarks_os: '',
				exemption_approved_remarks_os: ''
			},
			comments_endpoint_url: 'submission_remarks'
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
				endpoint_url: 'exemption_nomination_url',
				comments: {
					exemption_nomination_remarks_os: {
						name: 'exemption_nomination_remarks_os',
						selected: '',
						type: 'textarea',
						label: $gettext('Remarks (Secretariat)')
					}
				},
				get comments_array() {
					return getObjectLevel1PropertyValuesAsArray(this.comments)
				}
			},
			approved: {
				...getTabsCommonInfoForNominationAndApproved($gettext),
				name: 'approved',
				formNumber: 2,
				title: $gettext('Approved'),
				titleHtml: `<b>${$gettext('Approved')}</b>`,
				endpoint_url: 'exemption_approved_url',
				comments: {
					exemption_approved_remarks_os: {
						name: 'exemption_approved_remarks_os',
						selected: '',
						type: 'textarea',
						label: $gettext('Remarks (Secretariat)')
					}
				},
				get comments_array() {
					return getObjectLevel1PropertyValuesAsArray(this.comments)
				}
			}
		}
	}
	return form
}

export {
	getFormExemption
}
