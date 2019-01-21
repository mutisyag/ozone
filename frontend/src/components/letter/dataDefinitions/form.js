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
				fields_order: ['subject', ...tabSubInfo.fields_order],
				form_fields: {
					...tabSubInfo.form_fields,
					subject: {
						type: 'select',
						selected: 'c',
						options: [
							{ value: null, text: 'FOR TESTING ONLY Please select some item' },
							{ value: 'a', text: 'FOR TESTING ONLY This is First option' },
							{ value: 'b', text: 'FOR TESTING ONLY Default Selected Option' },
							{ value: 'c', text: 'FOR TESTING ONLY This is another option' },
							{ value: 'd', text: 'FOR TESTING ONLY This one is disabled', disabled: true }
						]
					}
				},
				default_properties: {
					...tabSubInfo.default_properties,
					subject: null
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
