const getAlerts = ($gettext) => {
  const alerts = {
    __all__: '',
    clone_success: $gettext('A clone of this submission has been added.'),
    cant_find_instructions: $gettext('Can\'t find instructions for current form'),
    save_before_submit: $gettext('Please save before submitting.'),
    questionaire_beforeSubmit: $gettext('Please complete the Questionnaire form before submitting.'),
    substance_already_exists: $gettext('Unable to add the following substances because they already exist'),
    select_country_before_adding_again: $gettext('select at least one country for each substance before adding.'),
    blend_already_exists: $gettext('Unable to add blend. Another blend with this name already exists.'),
    blend_not_added: $gettext('Unable to add the following blends because they already exist'),
    select_country_before_adding_again_blend: $gettext('select at least one country for each blend before adding.'),
    blend_created: $gettext('Custom blend added successfully.'),
    field_already_exists: $gettext('Unable to add fields for the following countries because they already exist'),
    save_failed: $gettext('Unable to save submission. Please try again.'),
    save_before_submitting: $gettext('Please save the document before submitting.'),
    new_version_created: $gettext('A clone of this submission has been added.')
  }
  return alerts
}

export {
  getAlerts
}
