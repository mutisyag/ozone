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
	selectTab,
	addSubstance,
	addBlend
} = require('../custom-methods/methods.js')

module.exports = {

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
	BU_006: browser => {
		login(browser, 'party', 'party')
		createSubmission(browser)
		clickQuestionnaireRadios(browser)
		selectTab(browser, 'Imports')
		addSubstance(browser, 'substance_selector', 'CFC-11')

		browser
			.useCss()
			.waitForElementVisible('.aside-menu .navbar-toggler', 10000)
			.moveToElement('aside.aside-menu > div > .navbar-toggler', undefined, undefined)
			.pause(500)
			.click('aside.aside-menu > div > .navbar-toggler')
			.pause(500)
			.moveToElement('#blends-table-title', undefined, undefined)
			.waitForElementVisible('#blends-table-title', 5000)
			.click('.badge.badge-danger.badge-pill')
			.pause(500)
			.click('aside.aside-menu > div > .navbar-toggler')
			.setValue('.submission-table tbody tr td:nth-child(4) input', 100)
			.setValue('.submission-table tbody tr td:nth-child(5) input', 5)
			.click('.submission-table tbody tr td:nth-child(2)')
			.assert.containsText('.validation-wrapper > span', 'valid')
		browser.execute('document.querySelector(".submission-table tbody tr").classList.add("hovered")', () => {
			browser
				.pause(5000)
				.click('.submission-table tbody tr td .row-controls span:not(.table-btn)')
		})
		browser
			.waitForElementVisible('#has_imports_tab .modal-body', 5000)
			.pause(500)
			.setValue('#has_imports_tab .modal-body #quantity_feedstock', 1)
			.setValue('#has_imports_tab .modal-body #quantity_critical_uses', 1)
			.setValue('#has_imports_tab .modal-body #decision_critical_uses', 'asd')
			.pause(5000)
			.click('#has_imports_tab .modal-dialog .close')
			.pause(500)
		addBlend(browser, 'blend_selector', 'R-401B')

		browser
			.pause(10000)
			.click('.app-footer .btn.btn-outline-danger')
			.pause(1000)
			.acceptAlert()
	}
}
