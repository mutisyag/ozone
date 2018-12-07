const getLevel2PropertyValue = (obj, level2PropertyKey) => {
	console.log('getLevel2PropertyValue')
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

export {
	getLevel2PropertyValue
}
