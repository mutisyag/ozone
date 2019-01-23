import { getTabSubInfo } from '@/components/common/dataDefinitions/tabSubInfo'
import { getTabAttachments } from '@/components/common/dataDefinitions/tabAttachments'

const getFormLetter = ($gettext) => {
	const tabSubInfo = getTabSubInfo($gettext)
	const form = {
		formDetails: {
			tabsDisplay: ['sub_info', 'attachments'],
			dataNeeded: [
				'initialData.countryOptions',
				'initialData.display.countries'
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
			attachments: getTabAttachments($gettext)
		}
	}
	return form
}

export {
	getFormLetter
}
