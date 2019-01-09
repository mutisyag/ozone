export default {
	substanceRows({
		section, substance, group, blend, prefillData, ordering_id
	}) {
		const baseInnerFields = {
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
			prop1: {
				type: 'number',
				selected: null
			},
			prop2: {
				type: 'number',
				selected: null
			},
			prop3: {
				type: 'number',
				selected: null
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
				if (!this.prop3.selected) {
					errors.push('Prop3 required')
				}

				const returnObj = {
					type: 'nonInput',
					selected: errors
				}

				return returnObj
			}
		}

		switch (section) {
		case 'has_imports':
			if (prefillData) {
				Object.keys(prefillData).forEach((field) => {
					baseInnerFields[field] ? baseInnerFields[field].selected = prefillData[field] : null
				})
			}
			return baseInnerFields
		case 'has_produced':
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
