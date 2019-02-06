import { getLabels } from '@/components/art7/dataDefinitions/labels'
import { fromExponential, isNumber } from '@/components/common/services/utilsService'

const getCountryField = (currentSection) => {
	switch (currentSection) {
	case 'has_exports':
		return 'destination_party'
	case 'has_imports':
		return 'source_party'
	default:
	}
}

const createTooltip = (fields, section, $gettext) => {
	let tooltip_title = ''
	if (Object.keys(fields).length) {
		Object.keys(fields).forEach(field => {
			tooltip_title += `${getLabels($gettext)[section][field]}: ${fields[field]}\n`
		})
	}
	tooltip_title += `\n ${$gettext('Click to edit')}`
	return tooltip_title
}

const quantityCalculator = (fields, parent, section, $gettext) => {
	let count = 0
	const returnObj = {
		type: 'nonInput',
		selected: count
	}

	const forTooltip = {}
	fields.filter(quantity => parent[quantity].selected)
		.forEach(quantity => {
			count += parseFloat(parent[quantity].selected)
			forTooltip[quantity] = parent[quantity].selected
		})

	if (count === 0) {
		returnObj.selected = ''
	} else {
		returnObj.selected = fromExponential(count)
	}

	const tooltip = createTooltip(forTooltip, section, $gettext)

	returnObj.tooltip = tooltip

	return returnObj
}

const valueConverter = (item) => {
	if (item === null || item === undefined || Number.isNaN(parseFloat(item))) {
		return 0
	}
	return parseFloat(item)
}

const doSum = (sumItems) => sumItems.reduce((sum, item) => valueConverter(item) + valueConverter(sum))

const decisionGenerator = (fields, parent, section, $gettext) => {
	const decisions = []
	const returnObj = {
		type: 'nonInput',
		selected: ''
	}
	const forTooltip = {}

	const decision_fields = fields

	decision_fields.filter(item => parent[item].selected)
		.forEach(item => {
			decisions.push(parent[item].selected)
			forTooltip[item] = parent[item].selected
		})

	const tooltip = createTooltip(forTooltip, section, $gettext)
	returnObj.tooltip = tooltip

	returnObj.selected = decisions.join(', ')
	return returnObj
}

export default {
	substanceRows({
		$gettext, section, substance, group, country, blend, prefillData, ordering_id
	}) {
		const countryFieldName = getCountryField(section)

		let baseInnerFields = {
			ordering_id: { selected: ordering_id || 0 },
			substance: {
				type: 'select',
				selected: substance || null
			},
			blend: {
				type: 'select',
				selected: blend || null,
				expand: false
			},
			group: {
				selected: group,
				type: 'nonInput'
			},
			quantity_total_new: {
				type: 'number',
				selected: null
			},
			quantity_total_recovered: {
				type: 'number',
				selected: null
			},
			quantity_feedstock: {
				type: 'number',
				selected: null
			},
			get quantity_exempted() {
				const fields = ['quantity_essential_uses', 'quantity_critical_uses', 'quantity_high_ambient_temperature', 'quantity_process_agent_uses', 'quantity_laboratory_analytical_uses', 'quantity_other_uses']
				return quantityCalculator(fields, this, section, $gettext)
			},

			get decision_exempted() {
				const fields = ['decision_essential_uses', 'decision_critical_uses', 'decision_high_ambient_temperature', 'decision_process_agent_uses', 'decision_laboratory_analytical_uses', 'decision_quarantine_pre_shipment', 'decision_polyols', 'decision_other_uses']
				return decisionGenerator(fields, this, section, $gettext)
			},
			quantity_essential_uses: {
				type: 'number',
				selected: null
			},
			decision_essential_uses: {
				type: 'text',
				selected: ''
			},
			quantity_critical_uses: {
				type: 'number',
				selected: null
			},
			decision_critical_uses: {
				type: 'text',
				selected: ''
			},
			quantity_high_ambient_temperature: {
				type: 'number',
				selected: null
			},
			decision_high_ambient_temperature: {
				type: 'text',
				selected: ''
			},
			quantity_process_agent_uses: {
				type: 'number',
				selected: null
			},
			decision_process_agent_uses: {
				type: 'text',
				selected: ''
			},
			quantity_laboratory_analytical_uses: {
				type: 'number',
				selected: null
			},
			decision_laboratory_analytical_uses: {
				type: 'text',
				selected: ''
			},
			quantity_quarantine_pre_shipment: {
				type: 'number',
				selected: null
			},
			decision_quarantine_pre_shipment: {
				type: 'text',
				selected: ''
			},
			quantity_other_uses: {
				type: 'number',
				selected: null
			},
			decision_other_uses: {
				type: 'text',
				selected: ''
			},
			quantity_polyols: {
				type: 'number',
				selected: null
			},
			decision_polyols: {
				type: 'text',
				selected: ''
			},
			remarks_party: {
				type: 'textarea',
				selected: ''
			},
			remarks_os: {
				type: 'textarea',
				selected: ''
			},
			get validation() {
				const errors = []
				if (doSum([this.quantity_total_new.selected, this.quantity_total_recovered.selected, this.quantity_polyols.selected]) <= 0) {
					errors.push($gettext('Total quantity imported for all uses is required'))
				}

				if (doSum([this.quantity_feedstock.selected, this.quantity_exempted.selected, this.quantity_quarantine_pre_shipment]) > doSum([this.quantity_total_new.selected, this.quantity_total_recovered.selected])) {
					errors.push($gettext('Total quantity imported for all uses must be >= to the sum of individual components'))
				}

				const returnObj = {
					type: 'nonInput',
					selected: errors
				}

				return returnObj
			}
		}

		baseInnerFields[countryFieldName] = {
			type: 'multiselect',
			selected: country || null
		}

		console.log('section', section)

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
				get quantity_exempted() {
					const fields = ['quantity_critical_uses', 'quantity_essential_uses', 'quantity_high_ambient_temperature', 'quantity_laboratory_analytical_uses', 'quantity_process_agent_uses', 'quantity_other_uses']
					return quantityCalculator(fields, this, section, $gettext)
				},
				get decision_exempted() {
					const fields = ['decision_critical_uses', 'decision_essential_uses', 'decision_high_ambient_temperature', 'decision_laboratory_analytical_uses', 'decision_process_agent_uses', 'decision_other_uses']
					return decisionGenerator(fields, this, section, $gettext)
				},
				quantity_critical_uses: {
					type: 'number',
					selected: null
				},
				decision_critical_uses: {
					type: 'text',
					selected: ''
				},
				quantity_essential_uses: {
					type: 'number',
					selected: null
				},
				decision_essential_uses: {
					type: 'text',
					selected: ''
				},
				quantity_high_ambient_temperature: {
					type: 'number',
					selected: null
				},
				decision_high_ambient_temperature: {
					type: 'text',
					selected: ''
				},
				quantity_laboratory_analytical_uses: {
					type: 'number',
					selected: null
				},
				decision_laboratory_analytical_uses: {
					type: 'text',
					selected: ''
				},
				quantity_process_agent_uses: {
					type: 'number',
					selected: null
				},
				decision_process_agent_uses: {
					type: 'text',
					selected: ''
				},
				quantity_quarantine_pre_shipment: {
					type: 'number',
					selected: null
				},
				decision_quarantine_pre_shipment: {
					type: 'text',
					selected: ''
				},
				quantity_total_produced: {
					type: 'number',
					selected: null
				},
				quantity_other_uses: {
					type: 'number',
					selected: null
				},
				decision_other_uses: {
					type: 'text',
					selected: ''
				},
				quantity_feedstock: {
					type: 'number',
					selected: null,
					colspan: 2
				},
				quantity_for_destruction: {
					type: 'number',
					selected: null
				},
				quantity_article_5: {
					type: 'number',
					selected: null
				},
				substance: {
					type: 'select',
					selected: substance || null
				},
				get validation() {
					const errors = []
					if (this.quantity_total_produced.selected === null) {
						errors.push($gettext('Column (3) should not be empty (total production for all uses / captured for all uses for FII)'))
					}

					if (this.group.selected && ['A', 'B', 'C', 'a', 'b', 'c'].includes(this.group.selected.split('')[0])) {
						if (valueConverter(this.quantity_total_produced.selected) < doSum([this.quantity_feedstock.selected, this.quantity_exempted.selected, this.quantity_article_5.selected])) {
							errors.push($gettext('For annexes A-C, total production (3) should be >= feedstock (4) + exempted, critical, other (5) + Article 5 countries (7)'))
						}
					}

					if (this.group.selected && ['E', 'e'].includes(this.group.selected.split('')[0])) {
						if (valueConverter(this.quantity_total_produced.selected) < doSum([this.quantity_feedstock.selected, this.quantity_exempted.selected, this.quantity_quarantine_pre_shipment.selected])) {
							errors.push($gettext('For annex E, total production (3) should be >= feedstock (4) + exempted, critical, other (5) + QPS'))
						}
					}

					if (this.group.selected && ['FI', 'fi'].includes(this.group.selected)) {
						if (valueConverter(this.quantity_total_produced.selected) < doSum([this.quantity_feedstock.selected, this.quantity_exempted.selected])) {
							errors.push($gettext('For annex F, total production (3) should be >= feedstock (4) + exempted, critical, other (5)'))
						}
					}

					if (this.group.selected && ['FII', 'fii'].includes(this.group.selected)) {
						if (valueConverter(this.quantity_total_produced.selected) < doSum([this.quantity_feedstock.selected, this.quantity_for_destruction.selected, this.quantity_exempted.selected])) {
							errors.push($gettext('For annex F2, total production (3) should be >= feedstock (4a) + destruction (4b) + exempted, critical, other (5)'))
						}
					}
					const returnObj = {
						type: 'nonInput',
						selected: errors
					}

					return returnObj
				}
			}
			break
		case 'has_destroyed':
			baseInnerFields = {
				ordering_id: { selected: ordering_id || 0 },
				substance: {
					type: 'select',
					selected: substance || null
				},
				blend: {
					type: 'select',
					selected: blend || null,
					expand: false
				},
				quantity_destroyed: {
					type: 'number',
					selected: null
				},
				group: {
					selected: group,
					type: 'nonInput'
				},
				remarks_party: {
					type: 'textarea',
					selected: ''
				},
				remarks_os: {
					type: 'textarea',
					selected: ''
				},
				get validation() {
					const errors = []
					if (valueConverter(this.quantity_destroyed.selected) === 0) {
						errors.push($gettext('Please complete the "Quantity destroyed (3)" field'))
					}

					const returnObj = {
						type: 'nonInput',
						selected: errors
					}

					return returnObj
				}
			}
			break
		case 'has_nonparty':
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
				quantity_import_new: {
					type: 'text',
					selected: null
				},
				quantity_import_recovered: {
					type: 'text',
					selected: null
				},
				quantity_export_new: {
					type: 'text',
					selected: null
				},
				quantity_export_recovered: {
					type: 'text',
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
				group: {
					selected: group,
					type: 'nonInput'
				},
				trade_party: {
					type: 'multiselect',
					selected: country || null
				},
				get validation() {
					const errors = []
					if (doSum([this.quantity_import_new.selected, this.quantity_import_recovered.selected, this.quantity_export_new.selected, this.quantity_export_recovered.selected]) <= 0) {
						errors.push($gettext('At least one field from (4), (5), (6), (7) is required'))
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
