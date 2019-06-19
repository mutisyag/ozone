import fromExponential from 'from-exponential/dist/index.min.js'
import { isNumber, doSum } from '@/components/common/services/utilsService'

const valueConverter = (item) => {
  if (item === null || item === undefined || Number.isNaN(parseFloat(item))) {
    return 0
  }
  return parseFloat(item)
}
const createTooltip = (fields, section, $gettext, countries) => {
  let tooltip_title = ''
  if (Object.keys(fields).length) {
    Object.keys(fields).forEach(field => {
      tooltip_title += `${countries[field]} : ${fromExponential(fields[field])}\n`
    })
  }
  tooltip_title += `\n ${$gettext('Click to edit')}`
  return tooltip_title
}

const quantityCalculator = (fields, parent, section, $gettext, countries) => {
  let count = 0
  const returnObj = {
    tooltip: '',
    type: 'nonInput',
    selected: count
  }

  const forTooltip = {}
  fields.forEach(field => {
    count = doSum([count, field.quantity])
    forTooltip[field.party] = valueConverter(field.quantity)
  })

  if (count === 0) {
    returnObj.selected = ''
  } else {
    returnObj.selected = fromExponential(count)
  }

  const tooltip = createTooltip(forTooltip, section, $gettext, countries)
  returnObj.tooltip = tooltip

  return returnObj
}

// eslint-disable-next-line no-unused-vars

export default {
  substanceRows({
    // eslint-disable-next-line no-unused-vars
    $gettext, section, substance, group, country, blend, prefillData, countries, critical, exemptionValue
  }) {
    const	baseInnerFields = {
      checkForDelete: {
        selected: false,
        type: 'checkbox'
      },
      remarks_party: {
        type: 'textarea',
        selected: ''
      },
      remarks_os: {
        type: 'textarea',
        selected: ''
      },
      group: {
        selected: group,
        type: 'nonInput'
      },
      substance: {
        type: 'select',
        selected: substance || null
      },
      quantity_exempted: {
        type: 'number',
        selected: null,
        exemptionValue
      },
      quantity_production: {
        type: 'number',
        selected: null
      },
      imports: [],
      get quantity_import() {
        return quantityCalculator(this.imports, this, section, $gettext, countries)
      },
      get quantity_acquired() {
        return {
          type: 'nonInput',
          selected: doSum([this.quantity_production.selected, this.quantity_import.selected])
        }
      },
      get quantity_authorized_not_acquired() {
        return {
          type: 'nonInput',
          selected: valueConverter(this.quantity_exempted.selected) - valueConverter(this.quantity_acquired.selected)
        }
      },
      on_hand_start_year: {
        type: 'number',
        selected: null
      },
      get available_for_use() {
        return {
          type: 'nonInput',
          selected: doSum([this.on_hand_start_year.selected, this.quantity_acquired.selected])
        }
      },
      is_emergency: {
        type: 'checkbox',
        selected: false
      },
      quantity_used: {
        type: 'number',
        selected: null
      },
      use_categories: {
        type: 'number',
        selected: null
      },
      quantity_exported: {
        type: 'number',
        selected: null
      },
      quantity_destroyed: {
        type: 'number',
        selected: null
      },
      get on_hand_end_year() {
        const criticalValue = critical ? valueConverter(this.quantity_exported.selected) : 0
        return {
          type: 'nonInput',
          selected: valueConverter(this.available_for_use.selected) - valueConverter(this.quantity_used.selected) - criticalValue - valueConverter(this.quantity_destroyed.selected)
        }
      },
      get validation() {
        const errors = []
        if (this.on_hand_end_year.selected === null) {
          errors.push($gettext('Please fill-in column On hand end of year (13)'))
        }

        const returnObj = {
          type: 'nonInput',
          selected: errors
        }

        return returnObj
      }
    }
    if (prefillData) {
      console.log('prefillData', prefillData)
      Object.keys(prefillData).forEach((field) => {
        if (Array.isArray(prefillData[field]) && field === 'imports') {
          baseInnerFields[field] = prefillData[field]
        }
        console.log(field)
        baseInnerFields[field]
          ?	baseInnerFields[field].selected = isNumber(prefillData[field])
            ? parseFloat(fromExponential(prefillData[field])) : prefillData[field]
          : null
      })
    }

    return baseInnerFields
  }

}
