import { expect } from 'chai'
import getters from '@/store/getters'

describe('store getters', () => {
	describe('can_edit_data', () => {
		const { can_edit_data } = getters
		it('missing permissions.form', () => {
			const state = {
				permissions: {
					form: null
				}
			}
			expect(can_edit_data(state)).to.be.null
		})
		it('value is equal to permissions.form.can_edit_data', () => {
			const state = {
				permissions: {
					form: {
						can_edit_data: true
					}
				}
			}
			expect(can_edit_data(state)).to.be.true
			state.permissions.form.can_edit_data = false
			expect(can_edit_data(state)).to.be.false
		})
	})
})
