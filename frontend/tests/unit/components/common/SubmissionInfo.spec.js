import Vue from 'vue'
import { expect } from 'chai'
import SubmissionInfo from '@/components/common/SubmissionInfo.vue'
import labels from '@/components/art7/dataDefinitions/labels'

describe('SubmissionInfo.vue', () => {
	it('has a created hook', () => {
		expect(SubmissionInfo.created).to.be.a('function')
	})

	it('sets the correct default data.labels', () => {
		expect(SubmissionInfo.data).to.be.a('function')
		const defaultData = SubmissionInfo.data()
		expect(defaultData.labels).to.be.null
	})

	it('correctly sets the data.labels when created', () => {
		const vm = new Vue(SubmissionInfo).$mount()
		expect(vm.labels).to.equal(labels.general)
	})
})
