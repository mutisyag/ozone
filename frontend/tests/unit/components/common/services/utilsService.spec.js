import { expect } from 'chai'
import {
	getLevel2PropertyValue,
	isObject,
	pushUnique,
	intersect,
	getPropertyValue,
	sortAscending,
	sortDescending
} from '@/components/common/services/utilsService'

describe('utilsService', () => {
	let testObj
	beforeEach(() => {
		testObj = {
			level1a: {
				level2a: 1,
				level2b: 2,
				level2c: 3
			},
			level1b: {
				level2d: 4,
				level2e: 5
			},
			level1c: {
				level2f: 6,
				level2g: {
					level3a: 7,
					level3b: 8
				}
			},
			level1d: 9
		}
	})

	describe('getLevel2PropertyValue', () => {
		it('for undefined and null', () => {
			expect(getLevel2PropertyValue(undefined, 'level2a')).to.be.undefined
			expect(getLevel2PropertyValue(null, 'level2a')).to.be.undefined
			expect(getLevel2PropertyValue(testObj)).to.be.undefined
			expect(getLevel2PropertyValue(testObj, null)).to.be.undefined
		})

		it('not existing level2PropertyKey', () => {
			expect(getLevel2PropertyValue(testObj, 'level2NotExisting')).to.be.undefined
			expect(getLevel2PropertyValue(testObj, 'level1b')).to.be.undefined
		})

		it('existing level2PropertyKey', () => {
			expect(getLevel2PropertyValue(testObj, 'level2a')).to.equal(1)
			expect(getLevel2PropertyValue(testObj, 'level2b')).to.equal(2)
			expect(getLevel2PropertyValue(testObj, 'level2c')).to.equal(3)
			expect(getLevel2PropertyValue(testObj, 'level2d')).to.equal(4)
			expect(getLevel2PropertyValue(testObj, 'level2e')).to.equal(5)
			expect(getLevel2PropertyValue(testObj, 'level2f')).to.equal(6)
		})
	})

	describe('isObject', () => {
		it('for undefined and null', () => {
			expect(isObject()).to.be.false
			const input = null
			expect(isObject(input)).to.be.false
		})
		it('for strings', () => {
			let input = ''
			expect(isObject(input)).to.be.false
			input = 'text'
			expect(isObject(input)).to.be.false
		})
		it('for numbers', () => {
			let input = 0
			expect(isObject(input)).to.be.false
			input = 2
			expect(isObject(input)).to.be.false
			input = 4.3
			expect(isObject(input)).to.be.false
		})
		it('for objects', () => {
			let input = {}
			expect(isObject(input)).to.be.true
			input = {
				x: 1
			}
			expect(isObject(input)).to.be.true
		})
	})

	describe('pushUnique', () => {
		let arrayNumbersInitial
		let arrayNumbers
		let arrayStringsInitial
		let arrayStrings
		let arrayObjectsInitial
		let arrayObjects
		let arrayMixedInitial
		let arrayMixed
		beforeEach(() => {
			arrayNumbersInitial = [1, 2.5, 4, 300, 0.3, 5]
			arrayNumbers = [...arrayNumbersInitial]
			arrayStringsInitial = ['word1', 'word2', 'word3']
			arrayStrings = [...arrayStringsInitial]
			arrayObjectsInitial = [{
				x: 1,
				y: 2
			}, {
				a: 'value 1',
				b: 'value 2'
			}]
			arrayObjects = [...arrayObjectsInitial]
			arrayMixedInitial = [1, { x: 1, y: 2 }, 3.41, 'word1']
			arrayMixed = [...arrayMixedInitial]
		})

		it('for undefined and null', () => {
			let array
			pushUnique(array, 1)
			expect(array).to.be.undefined
			array = null
			expect(array).to.be.null
		})

		it('for numberArray', () => {
			pushUnique(arrayNumbers, 1)
			expect(arrayNumbers).to.deep.equal(arrayNumbersInitial)
			pushUnique(arrayNumbers, 4)
			expect(arrayNumbers).to.deep.equal(arrayNumbersInitial)
			pushUnique(arrayNumbers, 0.3)
			expect(arrayNumbers).to.deep.equal(arrayNumbersInitial)
			pushUnique(arrayNumbers, 5)
			expect(arrayNumbers).to.deep.equal(arrayNumbersInitial)
			pushUnique(arrayNumbers, 7)
			expect(arrayNumbers).to.deep.equal([...arrayNumbersInitial, 7])
		})

		it('for arrayStrings', () => {
			pushUnique(arrayStrings, 'word1')
			expect(arrayStrings).to.deep.equal(arrayStringsInitial)
			pushUnique(arrayStrings, 'word2')
			expect(arrayStrings).to.deep.equal(arrayStringsInitial)
			pushUnique(arrayStrings, 'word3')
			expect(arrayStrings).to.deep.equal(arrayStringsInitial)
			pushUnique(arrayStrings, 'word4')
			expect(arrayStrings).to.deep.equal([...arrayStringsInitial, 'word4'])
		})

		it('for arrayObjects', () => {
			pushUnique(arrayObjects, arrayObjectsInitial[0])
			expect(arrayObjects).to.deep.equal(arrayObjectsInitial)
			pushUnique(arrayObjects, arrayObjectsInitial[1])
			expect(arrayObjects).to.deep.equal(arrayObjectsInitial)
			const obj = {
				prop1: 'value'
			}
			pushUnique(arrayObjects, obj)
			expect(arrayObjects).to.deep.equal([...arrayObjectsInitial, obj])
		})

		it('for arrayMixed add existing', () => {
			pushUnique(arrayMixed, arrayMixedInitial[0])
			expect(arrayMixed).to.deep.equal(arrayMixedInitial)
			pushUnique(arrayMixed, arrayMixedInitial[1])
			expect(arrayMixed).to.deep.equal(arrayMixedInitial)
			pushUnique(arrayMixed, arrayMixedInitial[2])
			expect(arrayMixed).to.deep.equal(arrayMixedInitial)
			pushUnique(arrayMixed, arrayMixedInitial[3])
			expect(arrayMixed).to.deep.equal(arrayMixedInitial)
		})

		it('for arrayMixed add new number', () => {
			pushUnique(arrayMixed, 10)
			expect(arrayMixed).to.deep.equal([...arrayMixedInitial, 10])
		})

		it('for arrayMixed add new string', () => {
			pushUnique(arrayMixed, 'word 100')
			expect(arrayMixed).to.deep.equal([...arrayMixedInitial, 'word 100'])
		})

		it('for arrayMixed add new object', () => {
			const obj = {
				prop2: true
			}
			pushUnique(arrayMixed, obj)
			expect(arrayMixed).to.deep.equal([...arrayMixedInitial, obj])
		})
	})

	describe('intersect', () => {
		it('for undefined and null', () => {
			expect(intersect()).to.be.empty
			expect(intersect(null, null)).to.be.empty
			expect(intersect([1, 2], null)).to.be.empty
			expect(intersect(null, [5])).to.be.empty
		})

		it('for arrays', () => {
			expect(intersect([1, 2, 3, 4], [])).to.be.empty
			expect(intersect([], [4, 5])).to.be.empty
			expect(intersect([{ x: 1, y: 2 }], [{ x: 1, y: 2 }])).to.be.empty
			expect(intersect([1], [1])).to.deep.equal([1])
			expect(intersect([1, 2, 3, 4], [2, 3, 5])).to.deep.equal([2, 3])
			expect(intersect(['word1', 'word2', 'word3'], ['word10', 'word2', 'word4'])).to.deep.equal(['word2'])
			const obj = { x: 4, y: 6 }
			expect(intersect([obj, 3, 8], [obj, 'word2', 3])).to.deep.equal([obj, 3])
		})
	})

	describe('getPropertyValue', () => {
		it('for undefined, null and non objects', () => {
			expect(getPropertyValue()).to.be.undefined
			expect(getPropertyValue(null)).to.be.undefined
			expect(getPropertyValue(undefined, null)).to.be.undefined
			expect(getPropertyValue(null, null)).to.be.undefined
			expect(getPropertyValue(undefined, { prop1: 1 })).to.be.undefined
			expect(getPropertyValue(null, { prop1: 1 })).to.be.undefined
			expect(getPropertyValue('prop1', 'text')).to.be.undefined
			expect(getPropertyValue('prop1', 3)).to.be.undefined
			expect(getPropertyValue('length', [])).to.be.undefined
		})

		it('for objects', () => {
			expect(getPropertyValue(testObj, 'notExistingProp')).to.be.undefined
			expect(getPropertyValue(testObj, 'level1d')).to.equal(9)
			expect(getPropertyValue(testObj, 'level1a.level2a')).to.equal(1)
			expect(getPropertyValue(testObj, 'level1b.level2e')).to.equal(5)
			expect(getPropertyValue(testObj, 'level1c.level2g.level3b')).to.equal(8)
			expect(getPropertyValue(testObj, 'level1c.level2g.level3b.')).to.be.undefined
		})
	})

	describe('sortAscending', () => {
		it('for undefined, null or not an array should return null', () => {
			expect(sortAscending()).to.be.null
			expect(sortAscending(null)).to.be.null
			expect(sortAscending({ value: 1 })).to.be.null
			expect(sortAscending({ value: 1 }, 'value')).to.be.null
		})

		it('for empty array', () => {
			expect(sortAscending([])).to.be.empty
			expect(sortAscending([], 'propName')).to.be.empty
		})

		it('for number arrays', () => {
			expect(sortAscending([2, 1, 5, 3, 4])).to.deep.equal([1, 2, 3, 4, 5])
			expect(sortAscending([2, 1, 5, 3, 4], 'propertyNameNotExisting')).to.deep.equal([2, 1, 5, 3, 4])
		})

		it('for string arrays', () => {
			expect(sortAscending(['2a', '1a', '5a', '3a', '4a'])).to.deep.equal(['1a', '2a', '3a', '4a', '5a'])
			expect(sortAscending(['2a', '1a', '5a', '3a', '4a'], 'propertyNameNotExisting')).to.deep.equal(['2a', '1a', '5a', '3a', '4a'])
		})

		it('for object arrays', () => {
			const inputArray = [{ name: 'b', value: 3 }, { name: 'a', value: 7 }, { name: 'c', value: 1 }, { name: 'd', value: 5 }]
			expect(sortAscending([...inputArray])).to.deep.equal([...inputArray])
			expect(sortAscending([...inputArray], null)).to.deep.equal([...inputArray])
			expect(sortAscending([...inputArray], 'propertyNameNotExisting')).to.deep.equal([...inputArray])
			expect(sortAscending([...inputArray], 'name')).to.deep.equal([{ name: 'a', value: 7 }, { name: 'b', value: 3 }, { name: 'c', value: 1 }, { name: 'd', value: 5 }])
			expect(sortAscending([...inputArray], 'value')).to.deep.equal([{ name: 'c', value: 1 }, { name: 'b', value: 3 }, { name: 'd', value: 5 }, { name: 'a', value: 7 }])
		})
	})

	describe('sortDescending', () => {
		it('for undefined, null or not an array should return null', () => {
			expect(sortDescending()).to.be.null
			expect(sortDescending(null)).to.be.null
			expect(sortDescending({ value: 1 })).to.be.null
			expect(sortDescending({ value: 1 }, 'value')).to.be.null
		})

		it('for empty array', () => {
			expect(sortDescending([])).to.be.empty
			expect(sortDescending([], 'propName')).to.be.empty
		})

		it('for number arrays', () => {
			expect(sortDescending([2, 1, 5, 3, 4])).to.deep.equal([5, 4, 3, 2, 1])
			expect(sortDescending([2, 1, 5, 3, 4], 'propertyNameNotExisting')).to.deep.equal([2, 1, 5, 3, 4])
		})

		it('for string arrays', () => {
			expect(sortDescending(['2a', '1a', '5a', '3a', '4a'])).to.deep.equal(['5a', '4a', '3a', '2a', '1a'])
			expect(sortDescending(['2a', '1a', '5a', '3a', '4a'], 'propertyNameNotExisting')).to.deep.equal(['2a', '1a', '5a', '3a', '4a'])
		})

		it('for object arrays', () => {
			const inputArray = [{ name: 'b', value: 3 }, { name: 'a', value: 7 }, { name: 'c', value: 1 }, { name: 'd', value: 5 }]
			expect(sortDescending([...inputArray])).to.deep.equal([...inputArray])
			expect(sortDescending([...inputArray], null)).to.deep.equal([...inputArray])
			expect(sortDescending([...inputArray], 'propertyNameNotExisting')).to.deep.equal([...inputArray])
			expect(sortDescending([...inputArray], 'name')).to.deep.equal([{ name: 'd', value: 5 }, { name: 'c', value: 1 }, { name: 'b', value: 3 }, { name: 'a', value: 7 }])
			expect(sortDescending([...inputArray], 'value')).to.deep.equal([{ name: 'a', value: 7 }, { name: 'd', value: 5 }, { name: 'b', value: 3 }, { name: 'c', value: 1 }])
		})
	})
})
