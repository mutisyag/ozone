import { expect } from 'chai'
import {
	getLevel2PropertyValue,
	isObject,
	pushUnique,
	intersect
} from '@/components/common/services/utilsService'

describe('utilsService', () => {
	describe('getLevel2PropertyValue', () => {
		const obj = {
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
				level2f: 6
			}
		}
		it('for undefined and null', () => {
			expect(getLevel2PropertyValue(undefined, 'level2a')).to.be.undefined
			expect(getLevel2PropertyValue(null, 'level2a')).to.be.undefined
			expect(getLevel2PropertyValue(obj)).to.be.undefined
			expect(getLevel2PropertyValue(obj, null)).to.be.undefined
		})

		it('not existing level2PropertyKey', () => {
			expect(getLevel2PropertyValue(obj, 'level2NotExisting')).to.be.undefined
			expect(getLevel2PropertyValue(obj, 'level1b')).to.be.undefined
		})

		it('existing level2PropertyKey', () => {
			expect(getLevel2PropertyValue(obj, 'level2a')).to.equal(1)
			expect(getLevel2PropertyValue(obj, 'level2b')).to.equal(2)
			expect(getLevel2PropertyValue(obj, 'level2c')).to.equal(3)
			expect(getLevel2PropertyValue(obj, 'level2d')).to.equal(4)
			expect(getLevel2PropertyValue(obj, 'level2e')).to.equal(5)
			expect(getLevel2PropertyValue(obj, 'level2f')).to.equal(6)
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
})
