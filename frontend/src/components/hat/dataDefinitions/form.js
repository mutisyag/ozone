import { getTabSubInfo } from '@/components/common/dataDefinitions/tabSubInfo'
import { setTabFiles } from '@/components/common/dataDefinitions/tabFiles'
import { getTabFlags } from '@/components/common/dataDefinitions/tabFlags'

const getFormHat = ($gettext) => {
  const form = {
    formDetails: {
      tabsDisplay: ['sub_info', 'has_imports', 'has_produced', 'files'],
      dataNeeded: [
        'initialData.countryOptions',
        'initialData.countryOptionsSubInfo',
        'initialData.substances',
        'initialData.blends',
        'current_submission',
        'initialData.display.substances',
        'initialData.display.blends',
        'initialData.display.countries',
        'initialData.submissionFormats',
        'currentUser',
        'permissions.form',
        'submissionDefaultValues.submission_format'
      ],
      comments_default_properties: {
        'hat_imports_remarks_party': '',
        'hat_imports_remarks_secretariat': '',
        'hat_production_remarks_party': '',
        'hat_production_remarks_secretariat': ''
      },
      comments_endpoint_url: 'submission_remarks'
    },
    tabs: {
      ...setTabFiles($gettext),
      sub_info: {
        ...getTabSubInfo($gettext),
        hideInfoButton: true,
        detailsHtml: $gettext('Respondents are requested to read the Introduction, the General Instructions, and the Definitions carefully before proceeding to the questionnaire and to refer to them as necessary when completing the data forms')
      },
      has_imports: {
        name: 'has_imports',
        hasAssideMenu: true,
        endpoint_url: 'hat_imports_url',
        ordering_id: 0,
        status: null,
        validate: true,
        saving: false,
        formNumber: 1,
        title: $gettext('Imports'),
        titleHtml: `<b>${$gettext('Consumption (imports)')}</b> <br><small>${$gettext('Annex F substances for exempted subsectors')} <br> ${$gettext('in metric tonnes (not ODP or CO2-equivalent tonnes)')}</small>`,
        detailsHtml: $gettext('Fill in this form only if your country is listed in appendix II to decision XXVIII/2, has formally notified the Secretariat of its intention to use the high-ambient-temperature exemption, and produced HFCs for its own use in the subsectors contained in appendix I to decision XXVIII/2'),
        isInvalid: false,
        form_fields: [],
        blend_substance_headers: ['substance', 'percent', 'quantity_msac', 'quantity_sdac', 'quantity_dcpac'],
        get fields_order() {
          return this.section_subheaders.map(x => x.name)
        },
        get input_fields() {
          return this.section_subheaders.filter(x => x.isInput).map(x => x.name)
        },
        section_subheaders: [{
          label: `(1)<br>${$gettext('Annex/Group')}`,
          name: 'group',
          sort: 1,
          colspan: 2,
          type: 'string'
        }, {
          label: `(2)<br>${$gettext('Substance')}`,
          name: 'substance',
          sort: 1,
          colspan: 2,
          type: 'string'
        }, {
          label: `(3)<br>${$gettext('New imports for use in multi-split air conditioners')}`,
          name: 'quantity_msac',
          isInput: true
        }, {
          label: `(4)<br>${$gettext('New imports for use in split ducted air conditioners')}`,
          name: 'quantity_sdac',
          isInput: true
        }, {
          label: `(5)<br>${$gettext('New imports for use in ducted commercial packaged (self-contained) air conditioners')}`,
          name: 'quantity_dcpac',
          isInput: true
        }, {
          label: `(6a)<br>${$gettext('Remarks (party')}`,
          name: 'remarks_party',
          isInput: true
        }, {
          label: `(6b)<br>${$gettext('Remarks (secretariat)')}`,
          name: 'remarks_os',
          isInput: true
        }, {
          label: `<br>${$gettext('Status')}`,
          name: 'validation'
        }
        ],

        section_headers: [{
          label: '',
          colspan: 2
        }, {
          label: $gettext('Quantity of new substances imported for approved subsectors to which the high-ambient-temperature exemption applies'),
          colspan: 3,
          tooltip: $gettext('Only bulk gases for servicing of exempted equipment should be reported here, not gases imported inside pre-charged equipment.')
        }, {
          label: '',
          colspan: 3
        }
        ],
        comments: {
          hat_imports_remarks_party: {
            name: 'hat_imports_remarks_party',
            selected: '',
            type: 'textarea'
          },
          hat_imports_remarks_secretariat: {
            name: 'hat_imports_remarks_secretariat',
            selected: '',
            type: 'textarea'
          }
        },
        default_properties: {
          'remarks_party': '',
          'remarks_os': '',
          'ordering_id': null,
          'quantity_msac': null,
          'quantity_sdac': null,
          'quantity_dcpac': null,
          'substance': null,
          'blend': null
        }
      },
      has_produced: {
        name: 'has_produced',
        hasAssideMenu: true,
        endpoint_url: 'hat_productions_url',
        ordering_id: 0,
        status: null,
        validate: true,
        saving: false,
        formNumber: 2,
        title: $gettext('Production'),
        titleHtml: `<b>${$gettext('PRODUCTION')}</b><br><small>${$gettext('Annex F substances for exempted subsectors')}<br>${$gettext('in metric tonnes (not ODP or CO2-equivalent tonnes)')}</small>`,
        detailsHtml: `1. ${$gettext('Fill in this form only if your country is listed in appendix II to decision XXVIII/2, has formally notified the Secretariat of its intention to use the high-ambient-temperature exemption, and produced HFCs for its own use in the subsectors contained in appendix I to decision XXVIII/2')}`,
        isInvalid: false,
        form_fields: [],
        blend_substance_headers: ['substance', 'percent', 'quantity_msac', 'quantity_sdac', 'quantity_dcpac'],
        get fields_order() {
          return this.section_subheaders.map(x => x.name)
        },
        get input_fields() {
          return this.section_subheaders.filter(x => x.isInput).map(x => x.name)
        },
        section_subheaders: [{
          label: `(1)<br>${$gettext('Annex/Group')}`,
          name: 'group',
          colspan: 2
        }, {
          label: `(2)<br>${$gettext('Substance')}`,
          name: 'substance',
          colspan: 2
        }, {
          label: `(3)<br>${$gettext('New production for use in multi-split air conditioners')}`,
          name: 'quantity_msac',
          isInput: true
        }, {
          label: `(4)<br>${$gettext('New production for use in split ducted air conditioners')}`,
          name: 'quantity_sdac',
          isInput: true
        }, {
          label: `(5)<br>${$gettext('New production for use in ducted commercial packaged (self-contained) air conditioners')}`,
          name: 'quantity_dcpac',
          isInput: true
        }, {
          label: `(6a)<br>${$gettext('Remarks (party')}`,
          name: 'remarks_party',
          isInput: true
        }, {
          label: `(6b)<br>${$gettext('Remarks (secretariat)')}`,
          name: 'remarks_os',
          isInput: true
        }, {
          label: `<br>${$gettext('Status')}`,
          name: 'validation'
        }],

        section_headers: [{
          label: '',
          colspan: 2
        }, {
          label: $gettext('Quantity of new substances produced for approved subsectors to which the high-ambient-temperature exemption applies (production should be for use within the producing country)'),
          colspan: 3,
          tooltip: $gettext('For each substance produced for use in subsectors that may be approved after the assessments under paragraphs 32 and 33 of decision XXVIII/2, please specify the approved subsector. Should the column space be insufficient, further information can be provided in the “comments” box above.')
        }, {
          label: '',
          colspan: 3
        }
        ],
        comments: {
          hat_production_remarks_party: {
            name: 'hat_production_remarks_party',
            selected: '',
            type: 'textarea'
          },
          hat_production_remarks_secretariat: {
            name: 'hat_production_remarks_secretariat',
            selected: '',
            type: 'textarea'
          }
        },
        default_properties: {
          'remarks_party': '',
          'remarks_os': '',
          'ordering_id': null,
          'quantity_msac': null,
          'quantity_sdac': null,
          'quantity_dcpac': null,
          'substance': null
        }
      },
      flags: getTabFlags($gettext)
    }
  }
  return form
}

export {
  getFormHat
}
