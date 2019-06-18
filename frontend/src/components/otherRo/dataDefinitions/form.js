import { getTabSubInfo } from '@/components/common/dataDefinitions/tabSubInfo'
import { setTabFiles } from '@/components/common/dataDefinitions/tabFiles'

const getFormOtherRo = ($gettext) => {
  const form = {
    formDetails: {
      tabsDisplay: ['sub_info', 'files', 'transfers'],
      dataNeeded: [
        'initialData.countryOptions',
        'initialData.countryOptionsSubInfo',
        'initialData.substances',
        'current_submission',
        'initialData.display.substances',
        'initialData.display.countries',
        'currentUser',
        'permissions.form'
      ],
      comments_default_properties: {
        'transfers_remarks_secretariat': ''
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
      transfers: {
        name: 'transfers',
        endpoint_url: 'transfers_url',
        status: null,
        skipSave: true,
        formNumber: 1,
        title: $gettext('Transfers'),
        titleHtml: `<b>${$gettext('Transfers')}</b> <br><small>${$gettext('Annex F substances for exempted subsectors')} <br> ${$gettext('in metric tonnes (not ODP or CO2-equivalent tonnes)')}</small>`,
        form_fields: [],
        comments: {
          transfers_remarks_secretariat: {
            selected: '',
            type: 'textarea'
          }
        },
        blend_substance_headers: ['substance', 'source_party', 'destination_party', 'transferred_amount', 'reporting_period', 'is_basic_domestic_need'],
        get fields_order() {
          return this.section_subheaders.map(x => x.name)
        },
        get input_fields() {
          return this.section_subheaders.filter(x => x.isInput).map(x => x.name)
        },
        section_subheaders: [{
          label: `(1)<br>${$gettext('Substance')}`,
          name: 'substance',
          colspan: 1,
          type: 'string'
        }, {
          label: `(2)<br>${$gettext('Source party')}`,
          name: 'source_party',
          isInput: true
        }, {
          label: `(3)<br>${$gettext('Destination party')}`,
          name: 'destination_party',
          isInput: true
        }, {
          label: `(4)<br>${$gettext('Transferred amount')}`,
          name: 'transferred_amount',
          isInput: true
        }, {
          label: `(5)<br>${$gettext('Reporting period')}`,
          name: 'reporting_period',
          isInput: true
        }, {
          label: `(6)<br>${$gettext('Basic domestic need')}`,
          name: 'is_basic_domestic_need',
          isInput: true
        }, {
          label: `(7)<br>${$gettext('Transfer type')}`,
          name: 'transfer_type',
          isInput: true
        }
        ],

        section_headers: [{
          label: '',
          colspan: 7
        }],
        default_properties: {
          'transfer_type': '',
          'source_party': '',
          'destination_party': null,
          'reporting_period': null,
          'substance': null,
          'transferred_amount': null,
          'is_basic_domestic_need': null
        }
      }
    }
  }
  return form
}

export {
  getFormOtherRo
}
