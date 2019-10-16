const setTabFiles = ($gettext) => ({
  files: {
    name: 'files',
    // endpoint_url is not used, but it is needed in order to not introduce another exception in the saving process
    endpoint_url: 'files_url',
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
    },
    validate: true,
    get validation() {
      return this.form_fields.files.length > 0
    }
  }
})
export {
  setTabFiles
}
