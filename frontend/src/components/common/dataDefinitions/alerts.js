const getAlerts = ($gettext) => {
  const alerts = {
    __all__: '',
    clone_success: $gettext('A new version of this submission has been added.'),
    cant_find_instructions: $gettext('No detailed instructions for the current form are available.'),
    save_before_submit: $gettext('You have unsaved changes. Please save the submission first.'),
    substance_already_exists: $gettext('Unable to add the following substances because they already exist'),
    select_country_before_adding_again: $gettext('select at least one country for each substance before adding.'),
    blend_already_exists: $gettext('Unable to add mixture. Another mixture with this name already exists.'),
    blend_not_added: $gettext('Unable to add the following mixtures because they already exist'),
    select_country_before_adding_again_blend: $gettext('select at least one country for each mixture before adding.'),
    blend_created: $gettext('Custom mixture added successfully.'),
    field_already_exists: $gettext('Unable to add rows for the following countries because they already exist'),
    save_failed: $gettext('Unable to save submission. Please try again.'),
    save_before_submitting: $gettext('You have unsaved changes. Please save the submission first.'),
    new_version_created: $gettext('A new version of this submission has been added.')
  }
  return alerts
}

export {
  getAlerts
}
