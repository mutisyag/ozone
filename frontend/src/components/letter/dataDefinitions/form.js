import { getTabSubInfo } from '@/components/common/dataDefinitions/tabSubInfo'
import { getTabFiles } from '@/components/common/dataDefinitions/tabFiles'

const getFormLetter = ($gettext) => {
	const tabSubInfo = getTabSubInfo($gettext)
	const form = {
		formDetails: {
			tabsDisplay: ['sub_info', 'files'],
			dataNeeded: [
				'initialData.countryOptions',
				'initialData.display.countries'
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
			files: getTabFiles($gettext)
		}
	}
	return form
}

export {
	getFormLetter
}
