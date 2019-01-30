/* eslint-disable func-style */
/* eslint-disable no-unused-vars */
// For authoring Nightwatch tests, see
// http://nightwatchjs.org/guide#usage

// or more concisely
const util = require('util')
const execSync = util.promisify(require('child_process').execSync)
const {
	login,
	logout,
	createSubmission,
	deleteSubmission,
	clickQuestionnaireRadios,
	selectTab,
	addEntity,
	addValues
} = require('../custom-methods/methods.js')

module.exports = {
	before: (browser, done) => {
		browser.resizeWindow(1480, 900, done)
	},

	beforeEach: () => {
		console.log('running backend')
		execSync('bash ../utility/setup_backend.sh', { env: process.env })
		console.log('done running backend')
	},
	afterEach: () => {
		console.log('running cleanup')
		execSync('bash ../utility/cleanup_backend.sh', { env: process.env })
		console.log('done running cleanup')
	},
	BU_001: browser => {
		login(browser, 'party', 'party')
		logout(browser)
	},
	BU_002: browser => {
		login(browser, 'party', 'party')
		createSubmission(browser)
		deleteSubmission(browser)
		logout(browser)
	},
	BU_006: browser => {
		login(browser, 'party', 'party')
		createSubmission(browser)
		clickQuestionnaireRadios(browser, ['#has_imports'])
		selectTab(browser, 'Imports')
		addEntity(browser, 'has_imports_tab', 'Substances', 'substance_selector', 'CFC-11')

		browser
			.useCss()
			.moveToElement('#has_imports_tab #blends-table-title', undefined, undefined)
			.waitForElementVisible('#has_imports_tab #blends-table-title', 5000)
		addValues(browser, '#substance-table', '#has_imports_tab')
		addEntity(browser, 'has_imports_tab', 'Blends', 'blend_selector', 'R-401B')

		browser
			.useCss()
			.moveToElement('#tab-comments', undefined, undefined)
		addValues(browser, '#blend-table', '#has_imports_tab')

		browser
			.pause(500)
			.click('.app-footer #save-button')
			.useXpath()
			.execute('document.body.scrollTop = 0;document.documentElement.scrollTop = 0')
			.waitForElementVisible('//div[contains(@class,"form-wrapper")]//div[contains(@class, "card-header")]//ul//li//div[contains(text(), "Imports")]//i[contains(@class, "fa-check-circle")]', 20000)
			.end()
	}
}
