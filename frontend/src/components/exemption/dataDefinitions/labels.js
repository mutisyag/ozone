const getLabels = ($gettext) => {
  const labels = {
    nomination: {
      exemption_nomination_remarks_secretariat: $gettext('Remarks (Secretariat)'),
      substance: $gettext('Substance'),
      group: $gettext('Group'),
      is_emergency: $gettext('Emergency'),
      quantity: `${$gettext('Quantity')} (${$gettext('in metric tons')})`,
      remarks_os: $gettext('Remarks')
    },
    approved: {
      exemption_approved_remarks_secretariat: $gettext('Remarks (Secretariat)'),
      substance: $gettext('Substance'),
      group: $gettext('Group'),
      is_emergency: $gettext('Emergency'),
      quantity: `${$gettext('Quantity')} (${$gettext('in metric tons')})`,
      remarks_os: $gettext('Remarks'),
      approved_teap_amount: $gettext('Amount recommended by TEAP'),
      decision_approved: $gettext('Decision')
    }
  }
  return labels
}

export {
  getLabels
}
