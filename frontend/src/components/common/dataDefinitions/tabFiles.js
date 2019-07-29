const setTabFiles = ($gettext) => ({
  files: {
    name: 'files',
    // endpoint_url: 'files_url',
    hideInfoButton: true,
    status: null,
    hasAssideMenu: false,
    title: $gettext('Files'),
    titleHtml: `<b>${$gettext('SUPPORTING DOCUMENTS')}</b>`,
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
