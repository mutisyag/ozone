const getTabsCommonInfoForNominationAndApproved = ($gettext) => {
	const tabsCommonInfo = {
		hasAssideMenu: true,
		hideInfoButton: true,
		endpoint_url: 'exemptionapproved_url',
		ordering_id: 0,
		validate: true,
		status: null,
		saving: false,
		formNumber: 2,
		intro: 'intro....................',
		// detailsHtml: $gettext('detailsHtml...........................'),
		tooltipForTitleHtml: $gettext('tooltipForTitleHtml................................'),
		subtitle: $gettext('subtitle............'),
		description: $gettext('description...............'),
		isInvalid: false,
		section_subheaders: [
			{
				label: `(1) <br> ${$gettext('Annex/Group')}`,
				name: 'group'
			},
			{
				label: `(2) <br> ${$gettext('Substance')}`,
				name: 'substance'
			},
			{
				label: `(3) <br> ${$gettext('Quantity')} (${$gettext('in metric tonnes')})`,
				name: 'quantity',
				isInput: true
			},
			{
				label: `(4) <br> ${$gettext('Remarks')}`,
				name: 'remarks_os',
				isInput: true
			},
			{
				label: `<br> ${$gettext('Status')}`,
				name: 'validation'
			}
		],
		get fields_order() {
			return this.section_subheaders.map(x => x.name)
		},
		get rowInputFields() {
			return this.section_subheaders
				.filter(x => x.isInput)
				.map(x => x.name)
		},
		section_headers: null,
		blend_substance_headers: null,
		form_fields: [],
		hidden_fields_order: null,
		footnotes: [`footnotes.............. [1] ${$gettext('Tonne = Metric ton.')}`],
		default_properties: {
			substance: null,
			quantity: null,
			remarks_os: null
		}
	}
	return tabsCommonInfo
}
export {
	getTabsCommonInfoForNominationAndApproved
}
