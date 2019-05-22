/* eslint-disable func-style */
/* eslint-disable no-unused-vars */
// For authoring Nightwatch tests, see
// http://nightwatchjs.org/guide#usage

// or more concisely
const util = require('util')
const execSync = util.promisify(require('child_process').execSync)
const {
  showMouse,
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
    login(browser, 'p_ro', 'p_ro')
    logout(browser)
    browser.end()
  },
  BU_002: browser => {
    login(browser, 'p_ro', 'p_ro')
    createSubmission(browser, 'HAT Exemption: Imports and Production', '2017', '')
    deleteSubmissionFake(browser)
    deleteSubmission(browser)
    logout(browser)
    browser.end()
  },
  BU_003: browser => {
    const data = {
      submissionInfo: {
        designation: 'test designation',
        organization: 'test organisation',
        postal_address: 'test address',
        country: 'France',
        phone: '+490000000',
        email: 'john.doe@gmail.com'
      },
      reporting_officer: 'test name'
    }

    const autocomplet = false;

    login(browser, 'p_ro', 'p_ro')
    createSubmission(browser, 'Article 7 - Data Reporting', '2018', '')
    openDashboard(browser)
    editSubmission(browser, 1)
    saveAndFail(browser, data.submissionInfo)
    fillSubmissionInfo(browser, data, autocomplet)
    clickQuestionnaireRadios(browser)
    saveSubmission(browser, ['Submission Info', 'Questionnaire'])
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

    login(browser, 'p_ro', 'p_ro')
    createSubmission(browser, 'Article 7 - Data Reporting', '2018', '')
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
    const data = {
      submissionInfo: {
        designation: 'test designation',
        organization: 'test organisation',
        postal_address: 'test address',
        country: 'France',
        phone: '+490000000',
        email: 'john.doe@gmail.com'
      },
      reporting_officer: 'test name'
    }

    login(browser, 'p_ro', 'p_ro')
    createSubmission(browser, 'Article 7 - Data Reporting', '2018', '')
    saveAndFail(browser, data.submissionInfo)
    fillSubmissionInfo(browser, data, false)
    clickQuestionnaireRadios(browser, [], false)
    saveSubmission(browser, ['Questionnaire'])
    logout(browser)
    browser.end()
  },
  BU_006: browser => {
    const row_values = {
      quantity_total_new: 0.12
    }
    const modal_values = {
      quantity_feedstock: 0.10,
      quantity_critical_uses: 0.01,
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
    

    login(browser, 'p_ro', 'p_ro')
    createSubmission(browser, 'Article 7 - Data Reporting', '2018', '')
    fillSubmissionInfo(browser, submissionInfo)
    clickQuestionnaireRadios(browser, ['has_imports'])
    addEntity(browser, 'has_imports_tab', 'substance', ['A/I Chlorofluorocarbons (CFCs)', 'CFC-11'])
    addValues(browser, 'substance-table', 'has_imports_tab', 1, row_values, modal_values)

    addEntity(browser, 'has_imports_tab', 'blend', ['Zeotrope', 'R-401B'])
    addValues(browser, 'blend-table', 'has_imports_tab', 1, row_values, modal_values)

    saveSubmission(browser, ['Questionnaire', 'Imports'])
    browser.end()
  },
  BU_007: browser => {
    const row_values = {
      quantity_total_new: 0.12
    }
    const modal_values = {
      quantity_feedstock: 0.10,
      quantity_critical_uses: 0.01,
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

    login(browser, 'p_ro', 'p_ro')
    createSubmission(browser, 'Article 7 - Data Reporting', '2018', '')
    fillSubmissionInfo(browser, submissionInfo)
    clickQuestionnaireRadios(browser, ['has_exports'])

    addEntity(browser, 'has_exports_tab', 'substance', ['A/I Chlorofluorocarbons (CFCs)', 'CFC-11'], 1, true)
    addValues(browser, 'substance-table', 'has_exports_tab', 1, row_values, modal_values)

    addEntity(browser, 'has_exports_tab', 'blend', ['Zeotrope', 'R-401A'], 1, true)
    addValues(browser, 'blend-table', 'has_exports_tab', 1, row_values, modal_values)

    addComment(browser, 'has_exports_tab', 'Hakuna Matata')
    saveSubmission(browser, ['Questionnaire', 'Exports'])
    browser.end()
  },
  BU_008: browser => {
    const row_values = {
      quantity_total_produced: 0.12
    }
    const modal_values = {
      quantity_feedstock: 0.10,
      quantity_critical_uses: 0.01,
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

    login(browser, 'p_ro', 'p_ro')
    createSubmission(browser, 'Article 7 - Data Reporting', '2018', '')
    fillSubmissionInfo(browser, submissionInfo)
    clickQuestionnaireRadios(browser, ['has_produced'])

    addEntity(browser, 'has_produced_tab', 'substance', ['A/I Chlorofluorocarbons (CFCs)', 'CFC-11'], 1, true)
    addValues(browser, 'substance-table', 'has_produced_tab', 1, row_values, modal_values)

    addEntity(browser, 'has_produced_tab', 'substance', ['F I/II Hydrofluorocarbons (HFCs)', 'HFC-23'], 1, true)
    addValues(browser, 'fii-table', 'has_produced_tab', 1, row_values, modal_values)

    addComment(browser, 'has_produced_tab', 'Hakuna Matata')
    saveSubmission(browser, ['Questionnaire', 'Production'])
    browser.end()
  },
  BU_009: browser => {
    const row_values = {
      quantity_destroyed: 0.12
    }
    const modal_values = {}
    const submissionInfo = {
      reporting_officer: 'test name',
      designation: 'test designation',
      organization: 'test organisation',
      postal_address: 'test address',
      country: 'France',
      phone: '+490000000',
      email: 'john.doe@gmail.com'
    }

    login(browser, 'p_ro', 'p_ro')
    createSubmission(browser, 'Article 7 - Data Reporting', '2018', '')
    fillSubmissionInfo(browser, submissionInfo)
    clickQuestionnaireRadios(browser, ['has_destroyed'])

    addEntity(browser, 'has_destroyed_tab', 'substance', ['A/I Chlorofluorocarbons (CFCs)', 'CFC-11'], 1, true)
    addValues(browser, 'substance-table', 'has_destroyed_tab', 1, row_values, modal_values)

    addEntity(browser, 'has_destroyed_tab', 'blend', ['Zeotrope', 'R-401A'], 1, true)
    addValues(browser, 'blend-table', 'has_destroyed_tab', 1, row_values, modal_values)

    addComment(browser, 'has_destroyed_tab', 'Hakuna Matata')
    saveSubmission(browser, ['Questionnaire', 'Destruction'])
    browser.end()
  },
  BU_010: browser => {
    const row_values = {
      quantity_import_new: 0.12,
      quantity_import_recovered: 0.12
    }
    const modal_values = {
      quantity_export_new: 0.05,
      quantity_export_recovered: 0.01 
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

    login(browser, 'p_ro', 'p_ro')
    createSubmission(browser, 'Article 7 - Data Reporting', '2018', '')
    fillSubmissionInfo(browser, submissionInfo)
    clickQuestionnaireRadios(browser, ['has_nonparty'])

    addEntity(browser, 'has_nonparty_tab', 'substance', ['A/I Chlorofluorocarbons (CFCs)', 'CFC-11'], 1, true)
    addValues(browser, 'substance-table', 'has_nonparty_tab', 1, row_values, modal_values)

    addEntity(browser, 'has_nonparty_tab', 'blend', ['Zeotrope', 'R-401A'], 1, true)
    addValues(browser, 'blend-table', 'has_nonparty_tab', 1, row_values, modal_values)

    addComment(browser, 'has_nonparty_tab', 'Hakuna Matata')
    saveSubmission(browser, ['Questionnaire', 'Nonparty'])
    browser.end()
  },
  BU_011: browser => {
    const row_values = {
      facility_name: 'CCT Facility',
      quantity_generated: 10,
      quantity_emitted: 10,

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

    login(browser, 'p_ro', 'p_ro')    
    createSubmission(browser, 'Article 7 - Data Reporting', '2018', '')
    fillSubmissionInfo(browser, submissionInfo)
    clickQuestionnaireRadios(browser, ['has_emissions'])

    addFacility(browser, 'facility-table', 'has_emissions_tab', 1, row_values, true)

    addComment(browser, 'has_emissions_tab', 'Hakuna Matata')
    saveSubmission(browser, ['Questionnaire', 'Emissions'])
	 	browser.end()
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
    login(browser, 'p_ro', 'p_ro')
    createSubmission(browser, 'Article 7 - Data Reporting', '2018', '')
    fillSubmissionInfo(browser, submissionInfo)
    clickQuestionnaireRadios(browser)
    selectTab(browser, 'Files')
    uploadeFile(browser, 'hello.pdf', '../../../../')
    saveSubmission(browser, ['Submission Info', 'Questionnaire'])
    browser.end()
  },
  BU_013: browser => {
    login(browser, 'p_ro', 'p_ro')
    createSubmission(browser, 'HAT Exemption: Imports and Production', '2018')
    deleteSubmission(browser)
    browser.end()
  },
  BU_014: browser => {
    login(browser, 'p_ro', 'p_ro')
    createSubmission(browser, 'HAT Exemption: Imports and Production', '2018')
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

    login(browser, 'p_ro', 'p_ro')
    createSubmission(browser, 'HAT Exemption: Imports and Production', '2018', '')
    fillSubmissionInfo(browser, submissionInfo)
    saveSubmission(browser, ['Submission Info'])
    checkSumbissionInfoFlags(browser)
    saveSubmission(browser, ['Submission Info'])
    logout(browser)
    browser.end()
  },
  BU_019: browser => {
    const group = 'A/I Chlorofluorocarbons (CFCs)'
    const name = 'CFC-11'
    const formula = 'CFCl3'

    login(browser, 'p_ro', 'p_ro')
    openLookupTable(browser, 'Substances')
    filterEntity(browser, 'controlled_substances', [group, name, formula])
    logout(browser)
    browser.end()
  },
  BU_020: browser => {
    const name = 'R-411B'
    const components = 'HCFC-22'

    login(browser, 'p_ro', 'p_ro')
    openLookupTable(browser, 'Blends')
    filterEntity(browser, 'blends', [name, components])
    logout(browser)
    browser.end()
  },
  BU_021: browser => {
    const name = 'Afghanistan'

    login(browser, 'p_ro', 'p_ro')
    openLookupTable(browser, 'Parties')
    filterEntity(browser, 'parties', [name])
    logout(browser)
    browser.end()
  },
  // BU_022: browser => {
  //   const submissions = [
  //     {
  //       name: 'Article 7 - Data Reporting',
  //       data: [{ year: '2018', party: 'Romania' }]
  //     },
  //     {
  //       name: 'Accounting for Essential and Critical uses (RAF)',
  //       data: [{ year: '2018', party: 'Algeria' }]
  //     },
  //     {
  //       name: 'HAT Exemption: Imports and Production',
  //       data: [{ year: '2018', party: 'Angola' }]
  //     },
  //     {
  //       name: 'Article 2 (p. 5, 5 bis, 7) - Transfer of production/consumption rights',
  //       data: [{ year: '2018', party: 'Argentina' }]
  //     },
  //     {
  //       name: 'Laboratory and analytical uses (dec. VI/9(p. 3) and annex II of 6th MOP report)',
  //       data: [{ year: '2017', party: 'Romania' }]
  //     },
  //     {
  //       name: 'Process agent uses (dec. X/14)',
  //       data: [{ year: '2017', party: 'Belarus' }]
  //     },
  //     {
  //       name: 'Article 4B - Licensing information',
  //       data: [{ year: '2018', party: 'Brazil' }]
  //     },
  //     {
  //       name: 'Article 9 - Research, development, public awareness and exchange of information',
  //       data: [{ year: '2017', party: 'China' }]
  //     },
  //     {
  //       name: 'Requests for changes in baseline data (decs. XIII/15(p. 5) and XV/19)',
  //       data: [{ year: '2018', party: 'Romania' }]
  //     }
  //   ]

  //   const scenarios = [
  //     {
  //       filters: ['', '', '', '2018', '2018'],
  //       first_row_expected: ['Article 7 - Data Reporting', '2018', 'Romania'],
  //       rows_number_expected: 6
  //     },
  //     {
  //       filters: ['', 'Accounting for Essential and Critical uses (RAF)', 'Algeria', '2018', '2018'],
  //       first_row_expected: ['Accounting for Essential and Critical uses (RAF)', '2018', 'Algeria'],
  //       rows_number_expected: 1
  //     },
  //     {
  //       filters: ['', '', 'Romania', '', ''],
  //       first_row_expected: ['Article 7 - Data Reporting', '2018', 'Romania'],
  //       rows_number_expected: 3
  //     },
  //     {
  //       filters: ['', '', 'Romania', '2017', '2017'],
  //       first_row_expected: ['Laboratory and analytical uses (dec. VI/9(p. 3) and annex II of 6th MOP report)', '2017', 'Romania'],
  //       rows_number_expected: 1
  //     },
  //     {
  //       filters: ['', 'Article 9 - Research, development, public awareness and exchange of information', '', '2017', '2018'],
  //       first_row_expected: ['Article 9 - Research, development, public awareness and exchange of information', '2017', 'China'],
  //       rows_number_expected: 1
  //     }
  //   ]

  //   login(browser, 'secretariat', 'secretariat')
	// 	showMouse(browser)
  //   submissions.forEach(submission => {
  //     submission.data.forEach(data => {
  //       createSubmission(browser, submission.name, data.year, data.party, true, true)
  //     })
  //   })

  //   /* Sort by obligation name */
  //   browser
  //     .useXpath()
  //     .waitForElementVisible("//table[@id='all-submissions-table']//thead//th[1]", 10000)
  //     .click("//table[@id='all-submissions-table']//thead//th[1]")
  //     .pause(200)
  //     .click("//table[@id='all-submissions-table']//thead//th[1]")
  //     .pause(500)

  //   scenarios.forEach(scenario => {
  //     filterSubmission(browser, 'all-submissions-table', scenario.filters, scenario.first_row_expected, scenario.rows_number_expected)
  //   })

  //   logout(browser)
  //   browser.end()
  // },
  BU_023: browser => {
    const row_values = {
      quantity_total_new: 0.12
    }
    const modal_values = {
      quantity_feedstock: 0.10,
      quantity_critical_uses: 0.01,
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

    login(browser, 'p_ro', 'p_ro')
    createSubmission(browser, 'Article 7 - Data Reporting', '2018')
		fillSubmissionInfo(browser, submissionInfo)
    clickQuestionnaireRadios(browser, ['has_exports'])

    addEntity(browser, 'has_exports_tab', 'substance', ['A/I Chlorofluorocarbons (CFCs)', 'CFC-11'], 1)
    addValues(browser, 'substance-table', 'has_exports_tab', 1, row_values, modal_values)

    addEntity(browser, 'has_exports_tab', 'substance', ['A/I Chlorofluorocarbons (CFCs)', 'CFC-12'], 1)
    rowIsEmpty(browser, 'substance-table', 'has_exports_tab', 2, row_values, modal_values)
		addValues(browser, 'substance-table', 'has_exports_tab', 2, row_values, modal_values)
		saveSubmission(browser, ['Submission Info'])

    logout(browser)
    browser.end()
  }
}
