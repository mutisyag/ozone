import { fromExponential, isNumber } from '@/components/common/services/utilsService'

const valueConverter = (item) => {
  if (item === null || item === undefined || Number.isNaN(parseFloat(item))) {
    return 0
  }
  return parseFloat(item)
}

const createTooltip = (approved_use, section, $gettext, critical_use_categories) => {
  let tooltip_title = ''
  approved_use.forEach(category => {
    tooltip_title += `${critical_use_categories[category.critical_use_category] || $gettext('Unspecified')} : ${fromExponential(category.quantity)}\n`
  })
  tooltip_title += `${$gettext('Click to edit or view critical uses categories')}`
  return tooltip_title
}

export default {
  substanceRows({
    $gettext, substance, group, prefillData, section, critical_use_categories, has_critical_uses
  }) {
    const baseInnerFields = {
      checkForDelete: {
        selected: false,
        type: 'checkbox'
      },
      substance: {
        type: 'select',
        selected: substance || null
      },
      group: {
        selected: group,
        type: 'nonInput'
      },
      decision_approved: {
        selected: '',
        type: 'text'
      },
      approved_teap_amount: {
        selected: null,
        type: 'number'
      },
      approved_uses: [],
      quantity: {
        type: 'number',
        selected: null
      },
      is_emergency: {
        type: 'checkbox',
        selected: false
      },
      remarks_os: {
        type: 'text',
        selected: ''
      },
      set quantity_use_categories(val) {
        if (has_critical_uses && section === 'approved') {
          this.quantity.icon = {
            tooltip: createTooltip(this.approved_uses, section, $gettext, critical_use_categories),
            fa: 'fa fa-info-circle fa-lg'
          }
        }
      },
      get validation() {
        const errors = []
        if (valueConverter(this.quantity.selected) <= 0) {
          errors.push($gettext('Please complete the "(3) Quantity" field'))
        }
        const returnObj = {
          type: 'nonInput',
          selected: errors
        }

        return returnObj
      }
    }
    /* prefillData is used to populate rows from server response.

		I think that when we create new rows prefillData shouldn't be null! It should be this.$store.state.form.tabs[this.tabName].default_properties
		and in formComponents/Add.vue, inside addSubstance we should call this.$store.dispatch('createSubstance') with  {prefillData: default_properties}
		now it is called with {prefillData: null}. I can't modify this now because it would break Art7  */

    if (prefillData) {
      Object.keys(prefillData).forEach((field) => {
        if (Array.isArray(prefillData[field]) && field === 'approved_uses') {
          baseInnerFields[field] = prefillData[field]
        } else if (baseInnerFields[field] && !baseInnerFields[field].selected) {
          if (isNumber(prefillData[field])) {
            baseInnerFields[field].selected = parseFloat(fromExponential(prefillData[field]))
          } else {
            baseInnerFields[field].selected = prefillData[field]
          }
        }
      })
    }
    baseInnerFields.quantity_use_categories = null
    return baseInnerFields
  }

}
