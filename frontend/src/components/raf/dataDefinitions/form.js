import { getTabSubInfo } from '@/components/common/dataDefinitions/tabSubInfo'
import { setTabFiles } from '@/components/common/dataDefinitions/tabFiles'
import { getTabFlags } from '@/components/common/dataDefinitions/tabFlags'

const getFormRaf = ($gettext) => {
  const form = {
    formDetails: {
      tabsDisplay: ['sub_info', 'files', 'essencrit'],
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
      sub_info: {
        ...getTabSubInfo($gettext),
        hideInfoButton: true,
        detailsHtml: $gettext('Respondents are requested to read the Introduction, the General Instructions, and the Definitions carefully before proceeding to the questionnaire and to refer to them as necessary when completing the data forms')
      },
      ...setTabFiles($gettext),
      essencrit: {
        name: 'essencrit',
        hasAssideMenu: true,
        endpoint_url: 'raf_url',
        ordering_id: 0,
        status: null,
        validate: true,
        saving: false,
        formNumber: 2,
        title: $gettext('Essential and critical uses'),
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

        get modal_order() {
          return this.section_subheaders.map(x => x.name).filter(x => !['year', 'substance', 'validation', 'imports'].includes(x))
        },
        section_subheaders: [{
          label: `A<br>${$gettext('Year')}`,
          name: 'year',
          colspan: 2
        }, {
          label: `B<br>${$gettext('Ozone depleting substances')}`,
          name: 'substance',
          colspan: 2
        }, {
          label: `C<br>${$gettext('Amount exempted')}`,
          name: 'quantity_exempted',
          isInput: true
        }, {
          label: `D<br>${$gettext('Amount acquired by production')}`,
          name: 'quantity_production',
          isInput: true
        }, {
          label: `E<br>${$gettext('Amount acquired by import & countries of manufacture')}`,
          name: 'quantity_import'
        }, {
          label: `F<br>${$gettext('Total acquired')} <br> (D+E)`,
          name: 'quantity_acquired'
        }, {
          label: `G<br>${$gettext('Authorized but not acquired')} <br> (C-F)`,
          name: 'quantity_authorized_not_acquired'
        }, {
          label: `H<br>${$gettext('On hand start of the year')}`,
          name: 'on_hand_start_year',
          isInput: true
        }, {
          label: `I<br>${$gettext('Available for use')}<br> (H+F)`,
          name: 'available_for_use',
          isInput: true
        }, {
          label: `J<br>${$gettext('Used for essential use')}`,
          name: 'quantity_used',
          isInput: true
        }, {
          label: `K<br>${$gettext('Quantity contained in exported product')}`,
          name: 'quantity_exported',
          isInput: true
        }, {
          label: `L<br>${$gettext('Amount destroyed')}`,
          name: 'quantity_destroyed',
          isInput: true
        }, {
          label: `M<br>${$gettext('On hand end of year')}<br>(I-J-L)`,
          name: 'on_hand_end_year'
        }, {
          label: `<br>${$gettext('Emergency')}`,
          name: 'is_emergency',
          isInput: true
        }, {
          label: `<br>${$gettext('Actions')}`,
          name: 'validation'
        }],
        section_subheaders_critical: [{
          label: `A<br>${$gettext('Year')}`,
          name: 'year',
          colspan: 2
        }, {
          label: `B<br>${$gettext('Amount exempted')}`,
          name: 'quantity_exempted',
          isInput: true
        }, {
          label: `C<br>${$gettext('Amount acquired by production')}`,
          name: 'quantity_production',
          isInput: true
        }, {
          label: `D<br>${$gettext('Amount acquired by import & countries of manufacture')}`,
          name: 'quantity_import'
        }, {
          label: `E<br>${$gettext('Total acquired')} <br> (C+D)`,
          name: 'quantity_acquired'
        }, {
          label: `F<br>${$gettext('Authorized but not acquired')} <br> (B-E)`,
          name: 'quantity_authorized_not_acquired'
        }, {
          label: `G<br>${$gettext('On hand start of the year')}`,
          name: 'on_hand_start_year',
          isInput: true
        }, {
          label: `H<br>${$gettext('Available for use')}<br> (E+G)`,
          name: 'available_for_use',
          isInput: true
        }, {
          label: `I<br>${$gettext('Amount used for critical use')}`,
          name: 'quantity_used',
          isInput: true
        }, {
          label: `J<br>${$gettext('Amount exported')}`,
          name: 'quantity_exported',
          isInput: true
        }, {
          label: `K<br>${$gettext('Amount destroyed')}`,
          name: 'quantity_destroyed',
          isInput: true
        }, {
          label: `L<br>${$gettext('On hand end of year')}<br>(H-I-J-K)`,
          name: 'on_hand_end_year'
        }, {
          label: `<br>${$gettext('Emergency')}`,
          name: 'is_emergency',
          isInput: true
        }, {
          label: `<br>${$gettext('Actions')}`,
          name: 'validation'
        }],
        section_headers: [{
          label: '',
          colspan: 17
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
          'imports': [],
          'remarks_party': '',
          'remarks_os': '',
          'ordering_id': null,
          'quantity_exempted': null,
          'quantity_production': null,
          'quantity_used': null,
          'quantity_exported': null,
          'quantity_destroyed': null,
          'on_hand_start_year': null,
          'substance': null,
          'is_emergency': null
        }
      },
      flags: {
        ...getTabFlags($gettext),
        get fields_order() {
          return Object.keys(this.default_properties)
        },
        default_properties: {
          flag_provisional: false,
          flag_valid: null,
          flag_superseded: false,
          flag_has_reported_a1: false,
          flag_has_reported_a2: false,
          flag_has_reported_b1: false,
          flag_has_reported_b2: false,
          flag_has_reported_b3: false,
          flag_has_reported_c1: false,
          flag_has_reported_c2: false,
          flag_has_reported_c3: false,
          flag_has_reported_e: false,
          flag_has_reported_f: false
        }
      }
    }
  }
  return form
}

export {
  getFormRaf
}
