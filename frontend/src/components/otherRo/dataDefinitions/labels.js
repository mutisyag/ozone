import { getCommonLabels } from '@/components/common/dataDefinitions/labels'

const getLabels = ($gettext) => {
  const labels = {
    common: getCommonLabels($gettext),
    transfers: {
      substance: $gettext('Substances'),
      application: $gettext('Application'),
      application_substance: $gettext('Substance'),
      transfer_type: $gettext('Transfer type'),
      source_party: $gettext('Source party'),
      destination_party: $gettext('Destination party'),
      remarks_os: $gettext('Remarks (Secretariat)'),
      remarks_party: $gettext('Remarks (Party)'),
      transferred_amount: $gettext('Transferred amount'),
      reporting_period: $gettext('Reporting period'),
      is_basic_domestic_need: $gettext('Basic domestic need'),
      transfers_remarks_secretariat: $gettext('Comments (Secretariat)')
    },
    procagent: {
      common: getCommonLabels($gettext),
      pa_uses_reported_remarks_secretariat: $gettext('Comments (Secretariat)')
    }
  }
  return labels
}

export {
  getLabels
}
