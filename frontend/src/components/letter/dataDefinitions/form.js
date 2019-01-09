import tab_sub_info from '@/components/common/dataDefinitions/tab_sub_info'
import tab_attachments from '@/components/common/dataDefinitions/tab_attachments'

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
			...tab_sub_info,
			fields_order: ['subject', ...tab_sub_info.fields_order],
			form_fields: {
				...tab_sub_info.form_fields,
				subject: {
					type: 'select',
					selected: 'c',
					options: [
						{ value: null, text: 'Please select some item' },
						{ value: 'a', text: 'This is First option' },
						{ value: 'b', text: 'Default Selected Option' },
						{ value: 'c', text: 'This is another option' },
						{ value: 'd', text: 'This one is disabled', disabled: true }
					]
				}
			},
			default_properties: {
				...tab_sub_info.default_properties,
				subject: null
			}
		},
		attachments: tab_attachments
	}
}
export default form
