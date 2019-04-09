import fromExponential from 'from-exponential/dist/index.min.js'
import { isNumber } from '@/components/common/services/utilsService'

const valueConverter = (item) => {
  if (item === null || item === undefined || Number.isNaN(parseFloat(item))) {
    return 0
  }
  return parseFloat(item)
}

// eslint-disable-next-line no-unused-vars
const doSum = (sumItems) => sumItems.reduce((sum, item) => valueConverter(item) + valueConverter(sum))

export default {
  substanceRows({
    // eslint-disable-next-line no-unused-vars
    $gettext, section, substance, group, country, blend, prefillData, ordering_id
  }) {
    let baseInnerFields = {}
    switch (section) {
    case 'has_produced':
      baseInnerFields = {
        ordering_id: { selected: ordering_id || 0 },
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
        quantity_msac: {
          type: 'number',
          selected: null
        },
        quantity_sdac: {
          type: 'number',
          selected: null
        },
        quantity_dcpac: {
          type: 'number',
          selected: null
        },
        substance: {
          type: 'select',
          selected: substance || null
        },
        blend: {
          type: 'select',
          selected: blend || null,
          expand: false
        },
        get validation() {
          const errors = []
          if (this.quantity_msac.selected === null) {
            errors.push($gettext('Column (3) should not be empty (total production for all uses / captured for all uses for FII)'))
          }

          const returnObj = {
            type: 'nonInput',
            selected: errors
          }

          return returnObj
        }
      }
      break
    case 'has_imports':
      baseInnerFields = {
        ordering_id: { selected: ordering_id || 0 },
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
        quantity_msac: {
          type: 'number',
          selected: null
        },
        quantity_sdac: {
          type: 'number',
          selected: null
        },
        quantity_dcpac: {
          type: 'number',
          selected: null
        },
        substance: {
          type: 'select',
          selected: substance || null
        },
        blend: {
          type: 'select',
          selected: blend || null,
          expand: false
        },
        get validation() {
          const errors = []
          if (this.quantity_msac.selected === null) {
            errors.push($gettext('Column (3) should not be empty (total production for all uses / captured for all uses for FII)'))
          }

          const returnObj = {
            type: 'nonInput',
            selected: errors
          }

          return returnObj
        }
      }
      break
    default:
      break
    }
    if (prefillData) {
      Object.keys(prefillData).forEach((field) => {
        baseInnerFields[field]
          ?	baseInnerFields[field].selected = isNumber(prefillData[field])
            ? parseFloat(fromExponential(prefillData[field])) : prefillData[field]
          : null
      })
    }
    return baseInnerFields
  }

}
