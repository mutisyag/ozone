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
	saveSubmission,
	saveAndFail,
	editSubmission,
	openDashboard,
	fillSubmissionInfo,
	clickQuestionnaireRadios,
	selectTab,
	addEntity,
	addValues,
	addComment
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
	// BU_001: browser => {
	// 	login(browser, 'party', 'party')
	// 	logout(browser)
	// 	browser.end()
	// },
	// BU_002: browser => {
	// 	login(browser, 'party', 'party')
	// 	createSubmission(browser)
	// 	deleteSubmission(browser)
	// 	logout(browser)
	// 	browser.end()
	// },
	// BU_003: browser => {
	// 	login(browser, 'party', 'party')
	// 	createSubmission(browser)
	// 	openDashboard(browser)
	// 	editSubmission(browser)
	// 	saveAndFail(browser)
	// 	clickQuestionnaireRadios(browser)
	// 	saveSubmission(browser)
	// 	logout(browser)
	// 	browser.end()
	// },
	// BU_004: browser => {
	// 	const submissionInfo = {
	// 		reporting_officer: 'test name',
	// 		designation: 'test designation',
	// 		organization: 'test organisation',
	// 		postal_code: 'test address',
	// 		country: 'France',
	// 		phone: '+490000000',
	// 		fax: '+490000000',
	// 		email: 'john.doe@gmail.com',
	// 		date: '01/11/2019'
	// 	}

	// 	login(browser, 'party', 'party')
	// 	createSubmission(browser)
	// 	clickQuestionnaireRadios(browser)
	// 	fillSubmissionInfo(browser, submissionInfo)
	// 	browser.useXpath()
	// 		.waitForElementVisible("//button[contains(@class, 'btn-info-outline')]", 10000)
	// 		.click("//button[contains(@class, 'btn-info-outline')]")
	// 		.pause(500)
	// 		.click("//div[@id='instructions_modal']//button//span[contains(text(), 'Close')]")
	// 		.pause(500)
	// 	logout(browser)
	// 	browser.end()
	// },
	// BU_005: browser => {
	// 	login(browser, 'party', 'party')
	// 	createSubmission(browser)
	// 	saveAndFail(browser)
	// 	clickQuestionnaireRadios(browser, [], false)
	// 	saveSubmission(browser)
	// 	logout(browser)
	// 	browser.end()
	// },
	// BU_006: browser => {
	// 	login(browser, 'party', 'party')
	// 	createSubmission(browser)
	// 	clickQuestionnaireRadios(browser, ['#has_imports'])
	// 	selectTab(browser, 'Imports')
	// 	addEntity(browser, 'has_imports_tab', 'Substances', 'substance_selector', 'CFC-11')

	// 	browser
	// 		.useCss()
	// 		.moveToElement('#has_imports_tab #blends-table-title', undefined, undefined)
	// 		.waitForElementVisible('#has_imports_tab #blends-table-title', 5000)
	// 	addValues(browser, '#substance-table', '#has_imports_tab')
	// 	addEntity(browser, 'has_imports_tab', 'Blends', 'blend_selector', 'R-401B')

	// 	browser
	// 		.useCss()
	// 		.moveToElement('#tab-comments', undefined, undefined)
	// 	addValues(browser, '#blend-table', '#has_imports_tab')

	// 	saveSubmission(browser)
	// 	browser.useXpath()
	// 		.execute('document.body.scrollTop = 0;document.documentElement.scrollTop = 0')
	// 		.waitForElementVisible('//div[contains(@class,"form-wrapper")]//div[contains(@class, "card-header")]//ul//li//div[contains(text(), "Imports")]//i[contains(@class, "fa-check-circle")]', 20000)
	// 		.end()
	// }
	BU_007: browser => {
		const row_values = ['', 0.0123, 0.12]
		const modal_values = {
			quantity_total_recovered: 100,
			quantity_feedstock: 5,
			quantity_critical_uses: 1,
			decision_critical_uses: 'Do that'
		}

		login(browser, 'party', 'party')
		createSubmission(browser)
		clickQuestionnaireRadios(browser, ['has_exports'])

		addEntity(browser, 'has_exports_tab', 'substance', 'AI', 'CFC-11', 1, true)
		addValues(browser, 'substance-table', 'has_exports_tab', 1, row_values, modal_values)

		addEntity(browser, 'has_exports_tab', 'blend', 'Zeotrope', 'R-401A', 1, true)
		addValues(browser, 'blend-table', 'has_exports_tab', 1, row_values, modal_values)

		addComment(browser, 'has_exports_tab', 'Hakuna Matata')
		saveSubmission(browser, ['Exports'])
	}
}
