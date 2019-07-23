import { getTabSubInfo } from '@/components/common/dataDefinitions/tabSubInfo'
import { setTabFiles } from '@/components/common/dataDefinitions/tabFiles'
import { getTabsCommonInfoForNominationAndApproved } from './tabsCommonInfoForNominationAndApproved'
import { getTabFlags } from '@/components/common/dataDefinitions/tabFlags'

const getFormExemption = ($gettext) => {
  const form = {
    formDetails: {
      tabsDisplay: ['sub_info', 'files', 'nomination', 'approved'],
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
        exemption_nomination_remarks_secretariat: '',
        exemption_approved_remarks_secretariat: ''
      },
      comments_endpoint_url: 'submission_remarks'
    },
    tabs: {
      ...setTabFiles($gettext),
      sub_info: {
        ...getTabSubInfo($gettext),
        filterOut: ['submission_format']
      },
      nomination: {
        ...getTabsCommonInfoForNominationAndApproved($gettext),
        name: 'nomination',
        formNumber: 1,
        status: null,
        title: $gettext('Nomination'),
        titleHtml: `<b>${$gettext('Nomination')}</b>`,
        endpoint_url: 'exemption_nomination_url',
        comments: {
          exemption_nomination_remarks_secretariat: {
            selected: '',
            type: 'textarea'
          }
        }
      },
      approved: {
        ...getTabsCommonInfoForNominationAndApproved($gettext),
        name: 'approved',
        formNumber: 2,
        status: null,
        title: $gettext('Approved'),
        titleHtml: `<b>${$gettext('Approved')}</b>`,
        endpoint_url: 'exemption_approved_url',
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
            label: `(3) <br> ${$gettext('Quantity')} (${$gettext('in metric tons')})`,
            name: 'quantity',
            isInput: true
          },
          {
            label: `(4) <br> ${$gettext('Emergency')}`,
            name: 'is_emergency',
            isInput: true
          },
          {
            label: `(5) <br> ${$gettext('Remarks')}`,
            name: 'remarks_os',
            isInput: true
          },
          {
            label: `(6) <br> ${$gettext('Decision')}`,
            name: 'decision_approved',
            isInput: true
          },
          {
            label: `(7) <br> ${$gettext('Amount recommended by TEAP')}`,
            name: 'approved_teap_amount',
            isInput: true
          },
          {
            label: `<br> ${$gettext('Actions')}`,
            name: 'validation'
          }
        ],
        comments: {
          exemption_approved_remarks_secretariat: {
            selected: '',
            type: 'textarea'
          }
        },
        get fields_order() {
          return this.section_subheaders.map(x => x.name)
        },
        get rowInputFields() {
          return this.section_subheaders
            .filter(x => x.isInput)
            .map(x => x.name)
        },
        default_properties: {
          substance: null,
          quantity: null,
          is_emergency: null,
          remarks_os: null,
          decision_approved: null,
          approved_teap_amount: null
        }
      },
      flags: {
        ...getTabFlags($gettext),
        form_fields: {
          flag_approved: {
            selected: false,
            type: 'checkbox',
            options: [
              { text: $gettext('Approved'), value: true },
              { text: $gettext('Not approved'), value: false }
            ],
            radioType: 'stacked',
            disabled: true
          }
        },
        default_properties: {
          flag_approved: false
        }
      }
    }
  }
  return form
}

export {
  getFormExemption
}
