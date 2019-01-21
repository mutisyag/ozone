import { getLabels } from '@/components/letter/dataDefinitions/labels'

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
	} else if (count < 0) {
		returnObj.selected = count.toPrecision(3)
	} else if (count > 999) {
		returnObj.selected = parseInt(count)
	} else {
		returnObj.selected = count.toPrecision(3)
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

const doSum = (sumItems) => sumItems.reduce((sum, item) => valueConverter(item) + sum)

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
	nonSubstanceRows({
		$gettext, currentSectionName, prefillData, ordering_id
	}) {
		let row
		switch (currentSectionName) {
		case 'has_emissions':
			row = {
				id: {
					selected: null
				},
				ordering_id: {
					selected: ordering_id || 0
				},
				facility_name: {
					type: 'text',
					selected: ''
				},
				quantity_generated: {
					type: 'number',
					selected: ''
				},
				quantity_feedstock: {
					type: 'number',
					selected: ''
				},
				quantity_destroyed: {
					type: 'number',
					selected: ''
				},
				quantity_emitted: {
					type: 'number',
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
					if (!this.facility_name.selected) {
						errors.push('error 1 test')
					}

					const returnObj = {
						type: 'nonInput',
						selected: errors
					}

					return returnObj
				}
			}
			if (prefillData) {
				console.log(prefillData)
				Object.keys(prefillData).forEach((element) => {
					row[element].selected = prefillData[element]
				})
			}
			return row
		case 'sub_info':
			row = {
				id: {
					selected: null
				},
				reporting_officer: {
					type: 'text',
					selected: ''
				},
				designation: {
					type: 'text',
					selected: ''
				},
				organization: {
					type: 'text',
					selected: ''
				},
				postal_code: {
					type: 'text',
					selected: ''
				},
				country: {
					type: 'text',
					selected: ''
				},
				phone: {
					type: 'text',
					selected: ''
				},
				fax: {
					type: 'text',
					selected: ''
				},
				email: {
					type: 'email',
					selected: ''
				},
				date: {
					type: 'date',
					selected: ''
				}
			}
			if (prefillData) {
				Object.keys(prefillData).forEach((element) => {
					row[element].selected = prefillData[element]
				})
			}
			return row
		default:
			break
		}
	},

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
				selected: group
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
				const fields = ['quantity_essential_uses', 'quantity_critical_uses', 'quantity_high_ambient_temperature', 'quantity_process_agent_uses', 'quantity_laboratory_analytical_uses', 'quantity_quarantine_pre_shipment', 'quantity_other_uses']
				return quantityCalculator(fields, this, section, $gettext)
			},

			get decision_exempted() {
				const fields = ['decision_essential_uses', 'decision_critical_uses', 'decision_high_ambient_temperature', 'decision_process_agent_uses', 'decision_laboratory_analytical_uses', 'decision_quarantine_pre_shipment', 'decision_other_uses']
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
				if (doSum([this.quantity_total_new.selected, this.quantity_total_recovered.selected]) <= 0) {
					errors.push($gettext('Total quantity imported for all uses is required'))
				}

				if (valueConverter(this.quantity_exempted.selected) > doSum([this.quantity_total_new.selected, this.quantity_total_recovered.selected])) {
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

		switch (section) {
		case 'has_exports':
			if (prefillData) {
				Object.keys(prefillData).forEach((field) => {
					baseInnerFields[field] ? baseInnerFields[field].selected = prefillData[field] : null
				})
			}
			return baseInnerFields
		case 'has_imports':
			if (prefillData) {
				Object.keys(prefillData).forEach((field) => {
					baseInnerFields[field] ? baseInnerFields[field].selected = prefillData[field] : null
				})
			}
			return baseInnerFields
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
					selected: group
				},
				get quantity_exempted() {
					const fields = ['quantity_critical_uses', 'quantity_essential_uses', 'quantity_high_ambient_temperature', 'quantity_laboratory_analytical_uses', 'quantity_process_agent_uses', 'quantity_quarantine_pre_shipment']
					return quantityCalculator(fields, this, section, $gettext)
				},
				get decision_exempted() {
					const fields = ['decision_critical_uses', 'decision_essential_uses', 'decision_high_ambient_temperature', 'decision_laboratory_analytical_uses', 'decision_process_agent_uses', 'decision_quarantine_pre_shipment']
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
				blend: {
					type: 'select',
					selected: blend || null,
					expand: false
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
					if (!this.substance.selected) {
						errors.push('eroare1')
					}

					const returnObj = {
						type: 'nonInput',
						selected: errors
					}

					return returnObj
				}
			}

			if (prefillData) {
				Object.keys(prefillData).forEach((field) => {
					baseInnerFields[field] ? baseInnerFields[field].selected = prefillData[field] : null
				})
			}
			return baseInnerFields
		case 'has_destroyed':
			baseInnerFields = {
				ordering_id: { selected: ordering_id || 0 },
				substance: {
					type: 'select',
					selected: substance || null
				},
				quantity_destroyed: {
					type: 'number',
					selected: null
				},
				group: {
					selected: group
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
					if (!this.substance.selected) {
						errors.push('eroare1')
					}

					const returnObj = {
						type: 'nonInput',
						selected: errors
					}

					return returnObj
				}
			}
			if (prefillData) {
				Object.keys(prefillData).forEach((field) => {
					baseInnerFields[field] ? baseInnerFields[field].selected = prefillData[field] : null
				})
			}
			return baseInnerFields
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
					selected: group
				},
				trade_party: {
					type: 'multiselect',
					selected: country || null
				},
				get validation() {
					const errors = []
					if (!this.quantity_export_new.selected) {
						errors.push('eroare1')
					}

					const returnObj = {
						type: 'nonInput',
						selected: errors
					}

					return returnObj
				}
			}
			if (prefillData) {
				Object.keys(prefillData).forEach((field) => {
					baseInnerFields[field] ? baseInnerFields[field].selected = prefillData[field] : null
				})
			}
			return baseInnerFields
		default:
			// statements_def
			return {}
		}
	}

}
