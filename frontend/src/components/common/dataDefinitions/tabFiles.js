const getTabFiles = ($gettext) => {
	const tabFiles = {
		name: 'files',
		hideInfoButton: true,
		hasAssideMenu: false,
		title: $gettext('Files'),
		titleHtml: $gettext('Files'),
		detailsHtml: '',
		default_properties: {
			files: []
		},
		form_fields: {
			files: []
		}
	}
	return tabFiles
}
export {
	getTabFiles
}
