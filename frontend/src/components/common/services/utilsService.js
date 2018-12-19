const getLevel2PropertyValue = (obj, level2PropertyKey) => {
	if (!obj || !level2PropertyKey) {
		return undefined
	}
	const level1Keys = Object.keys(obj)
	for (let i = 0; i < level1Keys.length; i += 1) {
		const level1Key = level1Keys[i]
		const propertyValue = obj[level1Key][level2PropertyKey]
		if (obj[level1Key][level2PropertyKey] !== undefined) {
			return propertyValue
		}
	}
	return undefined
}

const isObject = (value) => !!(value && typeof value === 'object' && value.constructor === Object)

const pushUnique = (array, item) => {
	if (!array) {
		return
	}
	if (array.indexOf(item) === -1) {
		array.push(item)
	}
}

const intersect = (a, b) => {
	const setA = new Set(a)
	const setB = new Set(b)
	const intersection = new Set([...setA].filter(x => setB.has(x)))
	return Array.from(intersection)
}

export {
	getLevel2PropertyValue,
	isObject,
	pushUnique,
	intersect
}
