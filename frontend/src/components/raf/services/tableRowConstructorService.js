import fromExponential from 'from-exponential/dist/index.min.js'
import { isNumber } from '@/components/common/services/utilsService'

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
			tooltip_title += `${countries[field]} : ${fields[field]}\n`
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
		count += valueConverter(field.quantity)
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
const doSum = (sumItems) => sumItems.reduce((sum, item) => valueConverter(item) + valueConverter(sum))

export default {
	substanceRows({
		// eslint-disable-next-line no-unused-vars
		$gettext, section, substance, group, country, blend, prefillData, ordering_id, countries, essen_crit_type
	}) {
		const	baseInnerFields = {
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
			substance: {
				type: 'select',
				selected: substance || null
			},
			quantity_exempted: {
				type: 'number',
				selected: null
			},
			essen_crit_type: {
				type: 'select',
				selected: null,
				options: essen_crit_type
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
					selected: valueConverter(doSum([this.on_hand_start_year.selected], [this.quantity_acquired.selected]))
				}
			},
			quantity_used: {
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
				return {
					type: 'nonInput',
					selected: valueConverter(this.available_for_use.selected) - valueConverter(this.quantity_used.selected) - valueConverter(this.quantity_destroyed.selected)
				}
			},
			get validation() {
				const errors = []
				if (this.on_hand_end_year.selected === null) {
					errors.push($gettext('Column (3) should not be empty (total production for all uses / captured for all uses for FII)'))
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
				baseInnerFields[field]
					?	baseInnerFields[field].selected = isNumber(prefillData[field])
						? parseFloat(fromExponential(prefillData[field])) : prefillData[field]
					: null
			})
		}

		return baseInnerFields
	}

}
