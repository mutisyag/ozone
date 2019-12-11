import { getTabSubInfo } from '@/components/common/dataDefinitions/tabSubInfo'
import { setTabFiles } from '@/components/otherRo/dataDefinitions/tabFiles'

const getFormOtherRo = ($gettext, formName) => {
  const sub_info_details_html = {
    'transfer': $gettext('Please fill in this form only if your country will transfer production/consumption rights in accordance with paragraphs 5,5 bis,7 of Article 2.'),
    'procagent': $gettext('Please fill in this form only if your country used controlled substances for process agent applications in accordance with decision X/14. Relevant decisions in filling in the form include: IV/12, X/14, XXI/3 and XXIII/7.')
  }
  const form = {
    formDetails: {
      tabsDisplay: ['sub_info', 'files', formName],
      dataNeeded: [
        'initialData.countryOptions',
        'initialData.countryOptionsSubInfo',
        'initialData.reportingChannel',
        'initialData.substances',
        'current_submission',
        'initialData.display.substances',
        'initialData.display.countries',
        'currentUser',
        'permissions.form',
        'submissionDefaultValues.reporting_channel'
      ]
    },
    comments_default_properties: {
      pa_uses_reported_remarks_secretariat: ''
    },
    comments_endpoint_url: 'submission_remarks',
    tabs: {
      ...setTabFiles($gettext),
      sub_info: {
        ...getTabSubInfo($gettext),
        hideInfoButton: true,
        detailsHtml: formName ? sub_info_details_html[formName] : $gettext('Please fill in mandatory fields.'),
        filterOut: ['submission_format']
      },
      transfer: {
        name: 'transfer',
        endpoint_url: 'transfers_url',
        status: null,
        skipSave: true,
        formNumber: 1,
        title: $gettext('Transfers'),
        titleHtml: `<b>${$gettext('TRANSFERS OF PRODUCTION/CONSUMPTION RIGHTS')}</b>`,
        detailsHtml: $gettext('This form shows transfer of production/consumption rights in accordance with paragraphs 5,5 bis,7 of Article 2.'),
        form_fields: [],
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
          label: `(6)<br>${$gettext('Basic domestic needs')}`,
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
      },
      procagent: {
        name: 'procagent',
        endpoint_url: 'pa_uses_reported_url',
        status: null,
        skipSave: true,
        formNumber: 1,
        title: $gettext('Process agent uses'),
        titleHtml: `<b>${$gettext('LIST OF USES OF CONTROLLED SUBSTANCES AS PROCESS AGENTS')}</b>`,
        detailsHtml: $gettext('This form shows controlled substances used for process agent applications in accordance with decision X/14.'),
        form_fields: [],
        get fields_order() {
          return this.section_subheaders.map(x => x.name)
        },
        get input_fields() {
          return this.section_subheaders.filter(x => x.isInput).map(x => x.name)
        },
        section_subheaders: [
          {
            label: `(1) <br> ${$gettext('Substance')}`,
            name: 'application_substance'
          }, {
            label: `(2) <br> ${$gettext('Process agent application')}`,
            name: 'application'
          }, {
            label: `(3)<br>${$gettext('Make-up or consumption')}`,
            name: 'makeup_quantity',
            class: 'text-right'
          }, {
            label: `(4)<br>${$gettext('Maximum emissions')}`,
            name: 'emissions',
            class: 'text-right'
          }, {
            label: `(5)<br>${$gettext('Unit')}`,
            name: 'units'
          }, {
            label: `(6)<br> ${$gettext('Containment technologies used to minimize emissions')}`,
            name: 'contain_technologies',
            class: ['text-left', 'brake-row']
          }, {
            label: `(7)<br>${$gettext('Remarks')}`,
            name: 'remark',
            class: 'text-left'
          }
        ],
        comments: {
          pa_uses_reported_remarks_secretariat: {
            selected: '',
            type: 'textarea'
          }
        },
        section_headers: [{
          label: '',
          colspan: 7
        }],
        default_properties: {
          'pa_uses_reported_remarks_secretariat': '',
          'application_substance': '',
          'application': '',
          'decision': '',
          'makeup_quantity': '',
          'emissions': '',
          'contain_technologies': [],
          'units': null,
          'remark': null
        }
      }
    }
  }
  return form
}

export {
  getFormOtherRo
}
