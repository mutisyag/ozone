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
	deleteSubmissionFake,
	deleteSubmission,
	saveSubmission,
	saveAndFail,
	editSubmission,
	openLookupTable,
	openDashboard,
	openGeneralInstructions,
	filterSubmission,
	filterEntity,
	fillSubmissionInfo,
	checkSumbissionInfoFlags,
	clickQuestionnaireRadios,
	selectTab,
	addEntity,
	addFacility,
	addValues,
	addComment,
	rowIsEmpty,
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
		createSubmission(browser, 'Article 7', '2018', '')
		deleteSubmissionFake(browser)
		deleteSubmission(browser)
		logout(browser)
		browser.end()
	},
	BU_003: browser => {
		login(browser, 'party', 'party')
		createSubmission(browser, 'Article 7', '2018', '')
		openDashboard(browser)
		editSubmission(browser, 1)
		saveAndFail(browser)
		clickQuestionnaireRadios(browser)
		saveSubmission(browser, ['Questionnaire'])
		logout(browser)
		browser.end()
	},
	BU_004: browser => {
		const submissionInfo = {
			reporting_officer: 'test name',
			designation: 'test designation',
			organization: 'test organisation',
			postal_address: 'test address',
			country: 'France',
			phone: '+490000000',
			email: 'john.doe@gmail.com'

		}

		login(browser, 'party', 'party')
		createSubmission(browser, 'Article 7', '2018', '')
		clickQuestionnaireRadios(browser)
		fillSubmissionInfo(browser, submissionInfo)
		saveSubmission(browser, ['Submission Info', 'Questionnaire'])
		checkSumbissionInfoFlags(browser)
		saveSubmission(browser, ['Submission Info', 'Questionnaire'])
		openGeneralInstructions(browser)
		logout(browser)
		browser.end()
	},
	BU_005: browser => {
		login(browser, 'party', 'party')
		createSubmission(browser, 'Article 7', '2018', '')
		saveAndFail(browser)
		clickQuestionnaireRadios(browser, [], false)
		saveSubmission(browser, ['Questionnaire'])
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
		const submissionInfo = {
			reporting_officer: 'test name',
			designation: 'test designation',
			organization: 'test organisation',
			postal_address: 'test address',
			country: 'France',
			phone: '+490000000',
			email: 'john.doe@gmail.com'

		}
		login(browser, 'party', 'party')
		createSubmission(browser, 'Article 7', '2018', '')
		clickQuestionnaireRadios(browser, ['has_imports'])
		fillSubmissionInfo(browser, submissionInfo)
		addEntity(browser, 'has_imports_tab', 'substance', ['AI', 'CFC-11'])
		addValues(browser, 'substance-table', 'has_imports_tab', 1, row_values, modal_values, start_column)

		addEntity(browser, 'has_imports_tab', 'blend', ['Zeotrope', 'R-401B'])
		addValues(browser, 'blend-table', 'has_imports_tab', 1, row_values, modal_values, start_column)

		saveSubmission(browser, ['Questionnaire', 'Imports'])
		browser.end()
	},
	BU_007: browser => {
		const row_values = [0.0123, 0.12]
		const modal_values = {
			quantity_feedstock: 0.10,
			quantity_critical_uses: 0.02,
			decision_critical_uses: 'Do that'
		}
		const submissionInfo = {
			reporting_officer: 'test name',
			designation: 'test designation',
			organization: 'test organisation',
			postal_address: 'test address',
			country: 'France',
			phone: '+490000000',
			email: 'john.doe@gmail.com'

		}
		const start_column = 4

		login(browser, 'party', 'party')
		createSubmission(browser, 'Article 7', '2018', '')
		clickQuestionnaireRadios(browser, ['has_exports'])
		fillSubmissionInfo(browser, submissionInfo)

		addEntity(browser, 'has_exports_tab', 'substance', ['AI', 'CFC-11'], 1, true)
		addValues(browser, 'substance-table', 'has_exports_tab', 1, row_values, modal_values, start_column)

		addEntity(browser, 'has_exports_tab', 'blend', ['Zeotrope', 'R-401A'], 1, true)
		addValues(browser, 'blend-table', 'has_exports_tab', 1, row_values, modal_values, start_column)

		addComment(browser, 'has_exports_tab', 'Hakuna Matata')
		saveSubmission(browser, ['Questionnaire', 'Exports'])
		browser.end()
	},
	BU_008: browser => {
		const row_values_e1 = [5, 3]
		const row_values_e2 = [10]
		const modal_values = {
			quantity_critical_uses: 0.02,
			decision_critical_uses: 'Do that'
		}
		const submissionInfo = {
			reporting_officer: 'test name',
			designation: 'test designation',
			organization: 'test organisation',
			postal_address: 'test address',
			country: 'France',
			phone: '+490000000',
			email: 'john.doe@gmail.com'

		}
		const start_column = 3

		login(browser, 'party', 'party')
		createSubmission(browser, 'Article 7', '2018', '')
		clickQuestionnaireRadios(browser, ['has_produced'])
		fillSubmissionInfo(browser, submissionInfo)

		addEntity(browser, 'has_produced_tab', 'substance', ['AI', 'CFC-11'], 1, true)
		addValues(browser, 'substance-table', 'has_produced_tab', 1, row_values_e1, modal_values, start_column)

		addEntity(browser, 'has_produced_tab', 'substance', ['FII', 'HFC-23'], 1, true)
		addValues(browser, 'fii-table', 'has_produced_tab', 1, row_values_e2, modal_values, start_column)

		addComment(browser, 'has_produced_tab', 'Hakuna Matata')
		saveSubmission(browser, ['Questionnaire', 'Production'])
		browser.end()
	},
	BU_009: browser => {
		const row_values_e1 = [100]
		const row_values_e2 = [10]
		const modal_values = {
			quantity_destroyed: 5
		}
		const start_column = 3
		const submissionInfo = {
			reporting_officer: 'test name',
			designation: 'test designation',
			organization: 'test organisation',
			postal_address: 'test address',
			country: 'France',
			phone: '+490000000',
			email: 'john.doe@gmail.com'

		}

		login(browser, 'party', 'party')
		createSubmission(browser, 'Article 7', '2018', '')
		clickQuestionnaireRadios(browser, ['has_destroyed'])
		fillSubmissionInfo(browser, submissionInfo)

		addEntity(browser, 'has_destroyed_tab', 'substance', ['AI', 'CFC-11'], 1, true)
		addValues(browser, 'substance-table', 'has_destroyed_tab', 1, row_values_e1, modal_values, start_column)

		addEntity(browser, 'has_destroyed_tab', 'blend', ['Zeotrope', 'R-401A'], 1, true)
		addValues(browser, 'blend-table', 'has_destroyed_tab', 1, row_values_e2, modal_values, start_column)

		addComment(browser, 'has_destroyed_tab', 'Hakuna Matata')
		saveSubmission(browser, ['Questionnaire', 'Destruction'])
		browser.end()
	},
	BU_010: browser => {
		const row_values = [0.0123, 0.12]
		const modal_values = {
			quantity_export_new: 2,
			quantity_export_recovered: 1
		}
		const submissionInfo = {
			reporting_officer: 'test name',
			designation: 'test designation',
			organization: 'test organisation',
			postal_address: 'test address',
			country: 'France',
			phone: '+490000000',
			email: 'john.doe@gmail.com'

		}
		const start_column = 4

		login(browser, 'party', 'party')
		createSubmission(browser, 'Article 7', '2018', '')
		clickQuestionnaireRadios(browser, ['has_nonparty'])
		fillSubmissionInfo(browser, submissionInfo)

		addEntity(browser, 'has_nonparty_tab', 'substance', ['AI', 'CFC-11'], 1, true)
		addValues(browser, 'substance-table', 'has_nonparty_tab', 1, row_values, modal_values, start_column)

		addEntity(browser, 'has_nonparty_tab', 'blend', ['Zeotrope', 'R-401A'], 1, true)
		addValues(browser, 'blend-table', 'has_nonparty_tab', 1, row_values, modal_values, start_column)

		addComment(browser, 'has_nonparty_tab', 'Hakuna Matata')
		saveSubmission(browser, ['Questionnaire', 'Nonparty'])
		browser.end()
	},
	BU_011: browser => {
		const row_values = ['CCT Facility', 10, '', '', '', '', '', 10]
		const start_column = 1
		const submissionInfo = {
			reporting_officer: 'test name',
			designation: 'test designation',
			organization: 'test organisation',
			postal_address: 'test address',
			country: 'France',
			phone: '+490000000',
			email: 'john.doe@gmail.com'

		}

		login(browser, 'party', 'party')
		createSubmission(browser, 'Article 7', '2018', '')
		clickQuestionnaireRadios(browser, ['has_emissions'])
		fillSubmissionInfo(browser, submissionInfo)

		addFacility(browser, 'facility-table', 'has_emissions_tab', 1, row_values, start_column, true)

		addComment(browser, 'has_emissions_tab', 'Hakuna Matata')
		saveSubmission(browser, ['Questionnaire', 'Emissions'])
	},
	BU_012: browser => {
		const submissionInfo = {
			reporting_officer: 'test name',
			designation: 'test designation',
			organization: 'test organisation',
			postal_address: 'test address',
			country: 'France',
			phone: '+490000000',
			email: 'john.doe@gmail.com'

		}
		login(browser, 'party', 'party')
		createSubmission(browser, 'Article 7', '2018', '')
		clickQuestionnaireRadios(browser)
		fillSubmissionInfo(browser, submissionInfo)
		selectTab(browser, 'Files')
		uploadeFile(browser, 'hello.pdf', '../../../../')
		saveSubmission(browser, ['Submission Info', 'Questionnaire'])
		browser.end()
	},
	BU_013: browser => {
		login(browser, 'party', 'party')
		createSubmission(browser, 'HAT Imports and Production', '2018')
		deleteSubmission(browser)
		browser.end()
	},
	BU_014: browser => {
		login(browser, 'party', 'party')
		createSubmission(browser, 'HAT Imports and Production', '2018')
		deleteSubmission(browser)
		browser.end()
	},
	BU_015: browser => {
		const submissionInfo = {
			reporting_officer: 'test name',
			designation: 'test designation',
			organization: 'test organisation',
			postal_address: 'test address',
			country: 'France',
			phone: '+490000000',
			email: 'john.doe@gmail.com'

		}

		login(browser, 'party', 'party')
		createSubmission(browser, 'HAT Imports and Production', '2018', '')
		fillSubmissionInfo(browser, submissionInfo)
		saveSubmission(browser, ['Submission Info'])
		checkSumbissionInfoFlags(browser)
		saveSubmission(browser, ['Submission Info'])
		logout(browser)
		browser.end()
	},
	BU_019: browser => {
		const group = 'AI'
		const name = 'CFC-11'
		const formula = 'CFCl3'

		login(browser, 'party', 'party')
		openLookupTable(browser, 'Controlled substances')
		filterEntity(browser, 'controlled_substances', [group, name, formula])
		logout(browser)
		browser.end()
	},
	BU_020: browser => {
		const name = 'R-411B'
		const components = 'HCFC-22'

		login(browser, 'party', 'party')
		openLookupTable(browser, 'Blends')
		filterEntity(browser, 'blends', [name, components])
		logout(browser)
		browser.end()
	},
	BU_021: browser => {
		const name = 'Afghanistan'

		login(browser, 'party', 'party')
		openLookupTable(browser, 'Parties')
		filterEntity(browser, 'parties', [name])
		logout(browser)
		browser.end()
	},
	// BU_022: browser => {
	// 	const submissions = [
	// 		{
	// 			name: 'Article 7',
	// 			data: [{ year: '2018', party: 'Romania' }, { year: '2017', party: 'Albania' }]
	// 		},
	// 		{
	// 			name: 'Essential and Critical uses (RAF)',
	// 			data: [{ year: '2018', party: 'Algeria' }]
	// 		},
	// 		{
	// 			name: 'HAT Imports and Production',
	// 			data: [{ year: '2018', party: 'Angola' }]
	// 		},
	// 		{
	// 			name: 'Transfer or addition of production or consumption',
	// 			data: [{ year: '2018', party: 'Argentina' }]
	// 		},
	// 		{
	// 			name: 'Laboratory and analytical uses',
	// 			data: [{ year: '2017', party: 'Romania' }]
	// 		},
	// 		{
	// 			name: 'Process agent uses',
	// 			data: [{ year: '2017', party: 'Belarus' }]
	// 		},
	// 		{
	// 			name: 'Licensing information',
	// 			data: [{ year: '2018', party: 'Brazil' }]
	// 		},
	// 		{
	// 			name: 'Research, development, public awareness and exchange of information',
	// 			data: [{ year: '2017', party: 'China' }]
	// 		},
	// 		{
	// 			name: 'Requests for changes in reported baseline data',
	// 			data: [{ year: '2018', party: 'Romania' }]
	// 		}
	// 	]

	// 	const scenarios = [
	// 		{
	// 			filters: ['', '', '', '2018', '2018'],
	// 			first_row_expected: ['Article 7', '2018', 'Romania'],
	// 			rows_number_expected: 6
	// 		},
	// 		{
	// 			filters: ['', 'Essential and Critical uses (RAF)', 'Algeria', '2018', '2018'],
	// 			first_row_expected: ['Essential and Critical uses (RAF)', '2018', 'Algeria'],
	// 			rows_number_expected: 1
	// 		},
	// 		{
	// 			filters: ['', '', 'Romania', '', ''],
	// 			first_row_expected: ['Article 7', '2018', 'Romania'],
	// 			rows_number_expected: 3
	// 		},
	// 		{
	// 			filters: ['', '', 'Romania', '2017', '2017'],
	// 			first_row_expected: ['Laboratory and analytical uses', '2017', 'Romania'],
	// 			rows_number_expected: 1
	// 		},
	// 		{
	// 			filters: ['', 'Research, development, public awareness and exchange of information', '', '2017', '2018'],
	// 			first_row_expected: ['Research, development, public awareness and exchange of information', '2017', 'China'],
	// 			rows_number_expected: 1
	// 		},
	// 		{
	// 			filters: ['', 'Research, development, public awareness and exchange of information', '', '2017', '2018'],
	// 			first_row_expected: ['Research, development, public awareness and exchange of information', '2017', 'China'],
	// 			rows_number_expected: 1
	// 		},
	// 		{
	// 			filters: ['', '', 'Romania', '2016', '2016'],
	// 			first_row_expected: ['There are no records to show'],
	// 			rows_number_expected: 1
	// 		}
	// 	]

	// 	login(browser, 'secretariat', 'secretariat')

	// 	submissions.forEach(submission => {
	// 		submission.data.forEach(data => {
	// 			createSubmission(browser, submission.name, data.year, data.party, true, true)
	// 		})
	// 	})

	// 	/* Sort by obligation name */
	// 	browser
	// 		.useXpath()
	// 		.waitForElementVisible("//table[@id='all-submissions-table']//thead//th[1]", 10000)
	// 		.click("//table[@id='all-submissions-table']//thead//th[1]")
	// 		.pause(200)
	// 		.click("//table[@id='all-submissions-table']//thead//th[1]")
	// 		.pause(500)

	// 	scenarios.forEach(scenario => {
	// 		filterSubmission(browser, 'all-submissions-table', scenario.filters, scenario.first_row_expected, scenario.rows_number_expected)
	// 	})

	// 	logout(browser)
	// 	browser.end()
	// },
	BU_023: browser => {
		const row_values = [0.0123, 0.12]
		const modal_values = {
			quantity_feedstock: 0.10,
			quantity_critical_uses: 0.02,
			decision_critical_uses: 'Do that'
		}
		const start_column = 4

		login(browser, 'party', 'party')
		createSubmission(browser, 'Article 7', '2018')
		clickQuestionnaireRadios(browser, ['has_exports'])

		addEntity(browser, 'has_exports_tab', 'substance', ['AI', 'CFC-11'], 1)
		addValues(browser, 'substance-table', 'has_exports_tab', 1, row_values, modal_values, start_column)

		addEntity(browser, 'has_exports_tab', 'substance', ['AI', 'CFC-12'], 1)
		rowIsEmpty(browser, 'substance-table', 'has_exports_tab', 2, row_values, modal_values, start_column)

		logout(browser)
		browser.end()
	}
}
