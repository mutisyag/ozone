import { fromExponential, isNumber } from '@/components/common/services/utilsService'

const valueConverter = (item) => {
  if (item === null || item === undefined || Number.isNaN(parseFloat(item))) {
    return 0
  }
  return parseFloat(item)
}

export default {
  substanceRows({
    $gettext, substance, group, ordering_id, prefillData
  }) {
    const baseInnerFields = {
      ordering_id: { selected: ordering_id || 0 },
      substance: {
        type: 'select',
        selected: substance || null
      },
      group: {
        selected: group,
        type: 'nonInput'
      },
      quantity: {
        type: 'number',
        selected: null
      },
      remarks_os: {
        type: 'text',
        selected: ''
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
        if (baseInnerFields[field] && !baseInnerFields[field].selected) {
          if (isNumber(prefillData[field])) {
            baseInnerFields[field].selected = parseFloat(fromExponential(prefillData[field]))
          } else {
            baseInnerFields[field].selected = prefillData[field]
          }
        }
      })
    }
    return baseInnerFields
  }

}
