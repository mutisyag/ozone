import { expect } from 'chai'
import sinon from 'sinon'
import actions from '@/store/actions'

describe('store actions', () => {
	describe('setAlert', () => {
		const { setAlert } = actions
		it('commit addAlertData', () => {
			const commit = sinon.spy()
			const state = {}
			setAlert({ commit, state }, {
				message: {
					error1: 'Error 1',
					error2: 'Error 2'
				},
				variant: 'error'
			})

			expect(commit.callCount).is.equal(2)

			expect(commit.args.length).is.equal(2)
			expect(commit.args[0]).to.deep.equal(['addAlertData',
				{ displayMessage: 'Error 1', variant: 'error' }])
			expect(commit.args[1]).to.deep.equal(['addAlertData',
				{ displayMessage: 'Error 2', variant: 'error' }])
		})
	})
})
