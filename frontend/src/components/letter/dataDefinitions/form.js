import { getTabSubInfo } from '@/components/common/dataDefinitions/tabSubInfo'
import { setTabFiles } from '@/components/letter/dataDefinitions/tabFiles'

const getFormLetter = ($gettext) => {
  const tabSubInfo = getTabSubInfo($gettext)
  const form = {
    formDetails: {
      tabsDisplay: ['sub_info', 'files'],
      dataNeeded: [
        'initialData.countryOptions',
        'initialData.countryOptionsSubInfo',
        'initialData.reportingChannel',
        'initialData.display.countries',
        'submissionDefaultValues.reporting_channel'
      ]
    },
    tabs: {
      ...setTabFiles($gettext),
      sub_info: {
        ...tabSubInfo,
        filterOut: ['submission_format']
      }
    }
  }
  return form
}

export {
  getFormLetter
}
