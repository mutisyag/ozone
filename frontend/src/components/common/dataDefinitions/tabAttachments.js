const getTabAttachments = ($gettext) => {
	const tabAttachments = {
		name: 'attachments',
		hasAssideMenu: false,
		title: $gettext('Attachments'),
		titleHtml: $gettext('Attachments'),
		detailsHtml: '',
		default_properties: {
			attachments: []
		},
		form_fields: {
			attachments: []
		}
	}
	return tabAttachments
}
export {
	getTabAttachments
}
