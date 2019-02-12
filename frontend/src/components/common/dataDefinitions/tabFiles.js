const setTabFiles = ($gettext) => ({
	files: {
		name: 'files',
		endpoint_url: 'files_url',
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
})
export {
	setTabFiles
}
