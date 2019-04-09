const getAlerts = ($gettext) => {
  const alerts = {
    __all__: '',
    clone_success: $gettext('New version created'),
    cant_find_instructions: $gettext('Can\'t find instructions for current form'),
    save_before_submit: $gettext('Please save before submitting'),
    questionaire_beforeSubmit: $gettext('Please complete the questionnaire submitting'),
    substance_already_exists: $gettext('The following substances were not added because they already exist'),
    select_country_before_adding_again: $gettext('select at least one country for each substance before adding it again'),
    blend_already_exists: $gettext('A blend with this name already exists!'),
    blend_not_added: $gettext('The following blends were not added because they already exist'),
    select_country_before_adding_again_blend: $gettext('select at least one country for each blend before adding it again'),
    blend_created: $gettext('Blend created'),
    field_already_exists: $gettext('The fields for these countries were not added because they already exist'),
    save_failed: $gettext('Save failed'),
    save_before_submitting: $gettext('Please save before submitting'),
    new_version_created: $gettext('New version created')
  }
  return alerts
}

export {
  getAlerts
}
