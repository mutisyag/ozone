const getLabels = ($gettext) => {
  const labels = {
    nomination: {
      exemption_nomination_remarks_secretariat: $gettext('Remarks (Secretariat)'),
      substance: $gettext('Substance'),
      group: $gettext('Group'),
      quantity: `${$gettext('Quantity')} (${$gettext('in metric tonnes')})`,
      remarks_os: $gettext('Remarks')
    },
    approved: {
      exemption_approved_remarks_secretariat: $gettext('Remarks (Secretariat)'),
      substance: $gettext('Substance'),
      group: $gettext('Group'),
      quantity: `${$gettext('Quantity')} (${$gettext('in metric tonnes')})`,
      remarks_os: $gettext('Remarks')
    }
  }
  return labels
}

export {
  getLabels
}
