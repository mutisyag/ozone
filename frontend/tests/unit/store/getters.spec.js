import { expect } from 'chai'
import getters from '@/store/getters'

describe('store getters', () => {
	describe('isReadOnly', () => {
		const { isReadOnly } = getters
		it('missing current_submission', () => {
			const state = {}
			expect(isReadOnly(state)).to.be.false
		})
		it('value is the negation of current_submission.data_changes_allowed', () => {
			const state = {
				current_submission: {
					data_changes_allowed: true
				}
			}
			expect(isReadOnly(state)).to.be.false
			state.current_submission.data_changes_allowed = false
			expect(isReadOnly(state)).to.be.true
		})
	})
})
