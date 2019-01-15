/* eslint-disable func-style */
/* eslint-disable no-unused-vars */
// For authoring Nightwatch tests, see
// http://nightwatchjs.org/guide#usage

// or more concisely
const util = require('util')
const execSync = util.promisify(require('child_process').execSync)
const {
	login,
	createSubmission,
	clickQuestionnaireRadios,
	selectTab
} = require('../custom-methods/methods.js')
// const getSelectElementByContent = require('../custom-assertions/customSelectors')

module.exports = {

	beforeEach: () => {
		console.log('running backend')
		// execSync('bash ../utility/setup_backend.sh', { env: process.env })
		console.log('done running backend')
	},
	afterEach: () => {
		console.log('running cleanup')
		// execSync('bash ../utility/cleanup_backend.sh', { env: process.env })
		console.log('done running cleanup')
	},
	BU_006: browser => {
		login(browser, 'party', 'party')
		createSubmission(browser)
		clickQuestionnaireRadios(browser)
		selectTab(browser, 'Imports')
	}
}
