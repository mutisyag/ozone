import tab_sub_info from '@/components/common/dataDefinitions/tab_sub_info'
import tab_attachments from '@/components/common/dataDefinitions/tab_attachments'

const form = {
	formDetails: {
		tabsDisplay: ['sub_info', 'attachments'],
		dataNeeded: [
			'initialData.countryOptions'
		]
	},
	tabs: {
		sub_info: tab_sub_info,
		attachments: tab_attachments
	}
}
export default form
