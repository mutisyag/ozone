import { expect } from 'chai'
import mutations from '@/store/mutations'

describe('store mutations', () => {
  describe('setTabStatus', () => {
    const { setTabStatus } = mutations
    it('changes status', () => {
      const state = {
        form: {
          tabs: {
            tab1: {
              status: 'invalid'
            }
          }
        }
      }
      setTabStatus(state, {
        tab: 'tab1',
        value: 'valid'
      })
      expect(state.form.tabs.tab1.status).to.equal('valid')
    })
  })
})
