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
	addFacility,
	addValues,
	addComment,
	uploadeFile
} = require('../custom-methods/methods.js')

module.exports = {
	beforeEach: (browser) => {
		browser.resizeWindow(1480, 900)
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
		browser.end()
	},
	BU_002: browser => {
		login(browser, 'party', 'party')
		createSubmission(browser)
		deleteSubmission(browser)
		logout(browser)
		browser.end()
	},
	BU_003: browser => {
		login(browser, 'party', 'party')
		createSubmission(browser)
		openDashboard(browser)
		editSubmission(browser)
		saveAndFail(browser)
		clickQuestionnaireRadios(browser)
		saveSubmission(browser)
		logout(browser)
		browser.end()
	},
	BU_004: browser => {
		const submissionInfo = {
			reporting_officer: 'test name',
			designation: 'test designation',
			organization: 'test organisation',
			postal_code: 'test address',
			country: 'France',
			phone: '+490000000',
			email: 'john.doe@gmail.com',
			date: '01/11/2019'
		}

		login(browser, 'party', 'party')
		createSubmission(browser)
		clickQuestionnaireRadios(browser)
		fillSubmissionInfo(browser, submissionInfo)
		browser.useXpath()
			.waitForElementVisible("//button[contains(@class, 'btn-info-outline')]", 10000)
			.click("//button[contains(@class, 'btn-info-outline')]")
			.pause(500)
			.click("//div[@id='instructions_modal']//button//span[contains(text(), 'Close')]")
			.pause(500)
		logout(browser)
		browser.end()
	},
	BU_005: browser => {
		login(browser, 'party', 'party')
		createSubmission(browser)
		saveAndFail(browser)
		clickQuestionnaireRadios(browser, [], false)
		saveSubmission(browser)
		logout(browser)
		browser.end()
	},
	BU_006: browser => {
		const row_values = [0.0123, 0.12]
		const modal_values = {
			quantity_feedstock: 0.10,
			quantity_critical_uses: 0.02,
			decision_critical_uses: 'Do that'
		}
		const start_column = 4

		login(browser, 'party', 'party')
		createSubmission(browser)
		clickQuestionnaireRadios(browser, ['has_imports'])

		addEntity(browser, 'has_imports_tab', 'substance', ['AI', 'CFC-11'])
		addValues(browser, 'substance-table', 'has_imports_tab', 1, row_values, modal_values, start_column)

		addEntity(browser, 'has_imports_tab', 'blend', ['Zeotrope', 'R-401B'])
		addValues(browser, 'blend-table', 'has_imports_tab', 1, row_values, modal_values, start_column)

		saveSubmission(browser, ['Imports'])

		browser.end()
	},
	BU_007: browser => {
		const row_values = [0.0123, 0.12]
		const modal_values = {
			quantity_feedstock: 0.10,
			quantity_critical_uses: 0.02,
			decision_critical_uses: 'Do that'
		}
		const start_column = 4

		login(browser, 'party', 'party')
		createSubmission(browser)
		clickQuestionnaireRadios(browser, ['has_exports'])

		addEntity(browser, 'has_exports_tab', 'substance', ['AI', 'CFC-11'], 1, true)
		addValues(browser, 'substance-table', 'has_exports_tab', 1, row_values, modal_values, start_column)

		addEntity(browser, 'has_exports_tab', 'blend', ['Zeotrope', 'R-401A'], 1, true)
		addValues(browser, 'blend-table', 'has_exports_tab', 1, row_values, modal_values, start_column)

		addComment(browser, 'has_exports_tab', 'Hakuna Matata')
		saveSubmission(browser, ['Exports'])

		browser.end()
	},
	BU_008: browser => {
		const row_values_e1 = [5, 3]
		const row_values_e2 = [10]
		const modal_values = {
			quantity_critical_uses: 0.02,
			decision_critical_uses: 'Do that'
		}
		const start_column = 3

		login(browser, 'party', 'party')
		createSubmission(browser)
		clickQuestionnaireRadios(browser, ['has_produced'])

		addEntity(browser, 'has_produced_tab', 'substance', ['AI', 'CFC-11'], 1, true)
		addValues(browser, 'substance-table', 'has_produced_tab', 1, row_values_e1, modal_values, start_column)

		addEntity(browser, 'has_produced_tab', 'substance', ['FII', 'HFC-23'], 1, true)
		addValues(browser, 'fii-table', 'has_produced_tab', 1, row_values_e2, modal_values, start_column)

		addComment(browser, 'has_produced_tab', 'Hakuna Matata')
		saveSubmission(browser, ['Production'])

		browser.end()
	},
	BU_009: browser => {
		const row_values_e1 = [100]
		const row_values_e2 = [10]
		const modal_values = {
			quantity_destroyed: 5
		}
		const start_column = 3

		login(browser, 'party', 'party')
		createSubmission(browser)
		clickQuestionnaireRadios(browser, ['has_destroyed'])

		addEntity(browser, 'has_destroyed_tab', 'substance', ['AI', 'CFC-11'], 1, true)
		addValues(browser, 'substance-table', 'has_destroyed_tab', 1, row_values_e1, modal_values, start_column)

		addEntity(browser, 'has_destroyed_tab', 'blend', ['Zeotrope', 'R-401A'], 1, true)
		addValues(browser, 'blend-table', 'has_destroyed_tab', 1, row_values_e2, modal_values, start_column)

		addComment(browser, 'has_destroyed_tab', 'Hakuna Matata')
		saveSubmission(browser, ['Destruction'])

		browser.end()
	},
	BU_010: browser => {
		const row_values = [0.0123, 0.12]
		const modal_values = {
			quantity_export_new: 2,
			quantity_export_recovered: 1
		}
		const start_column = 4

		login(browser, 'party', 'party')
		createSubmission(browser)
		clickQuestionnaireRadios(browser, ['has_nonparty'])

		addEntity(browser, 'has_nonparty_tab', 'substance', ['AI', 'CFC-11'], 1, true)
		addValues(browser, 'substance-table', 'has_nonparty_tab', 1, row_values, modal_values, start_column)

		addEntity(browser, 'has_nonparty_tab', 'blend', ['Zeotrope', 'R-401A'], 1, true)
		addValues(browser, 'blend-table', 'has_nonparty_tab', 1, row_values, modal_values, start_column)

		addComment(browser, 'has_nonparty_tab', 'Hakuna Matata')
		saveSubmission(browser, ['Nonparty'])

		browser.end()
	},
	BU_011: browser => {
		const row_values = ['CCT Facility', 10, '', '', '', '', '', 10]
		const start_column = 1

		login(browser, 'party', 'party')
		createSubmission(browser)
		clickQuestionnaireRadios(browser, ['has_emissions'])

		addFacility(browser, 'facility-table', 'has_emissions_tab', 1, row_values, start_column, true)

		addComment(browser, 'has_emissions_tab', 'Hakuna Matata')
		saveSubmission(browser, ['Emissions'])

		browser.end()
	},
	BU_012: browser => {
		login(browser, 'party', 'party')
		createSubmission(browser)
		clickQuestionnaireRadios(browser)
		selectTab(browser, 'Files')
		uploadeFile(browser)

		saveSubmission(browser)
		browser.end()
	}
}
