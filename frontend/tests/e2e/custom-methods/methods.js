const logMessage = (browser, message) => {
	browser.perform((done) => {
		console.log('==================================================================')
		console.log(message)
		console.log('==================================================================')
		done()
	})
}

const login = (browser, username, password) => {
	logMessage(browser, "Log in with " + username + ":" + password)

  browser.url(process.env.VUE_DEV_SERVER_URL)
    .useCss()
    .waitForElementVisible('#id_username', 20000)
    .setValue('#id_username', username)
    .setValue('#id_password', password)
    .waitForElementVisible('input[type="submit"]', 10000)
    .pause(1000)
    .click('input[type="submit"]')
    .waitForElementVisible('h3', 8000)
    .assert.urlContains('/reporting/dashboard')
}

const logout = (browser) => {
	logMessage(browser, 'Log out')
  browser.useCss()
    .waitForElementVisible('header.app-header .navbar-nav a.dropdown-toggle', 5000)
    .click('header.app-header .navbar-nav a.dropdown-toggle')
    .waitForElementVisible('#logout_button', 5000)
    .click('#logout_button')
    .waitForElementVisible('#id_username', 5000)
    .assert.urlContains('/admin/login')
}

const setMultiSelector = (browser, selector_id, option, singleSelectWithText = true) => {
  const time = 20000
  let multiselectSingle = '';

  if (singleSelectWithText) {
    multiselectSingle = `//div[@id='${selector_id}']//span[contains(@class, 'multiselect__single') and contains(text(), '${option}')]`
  } else {
    multiselectSingle = `//div[@id='${selector_id}']//span[contains(@class, 'multiselect__single')]//span[contains(text(), '${option}')]`
  }

  browser
    .useXpath()
    /* Check if multiselect is visible */
    .waitForElementVisible(`//div[@id = '${selector_id}']//div[@class = 'multiselect']`, time)
    
    .element('xpath', multiselectSingle, (result) => {
      if (result.status === -1) {
        browser
          /* Open multiselect */
          .click(`//div[@id = '${selector_id}']//div[@class = 'multiselect']`)
          .pause(1000)
          /* Check if multiselect is opened */
          .waitForElementVisible(`//div[@id = '${selector_id}']//div[@class = 'multiselect__content-wrapper']`, time)
          /* Check if desired option is visible */
          .waitForElementVisible(`//div[@id = '${selector_id}']//div[@class = 'multiselect__content-wrapper']//ul//li//span//span[contains(text(),'${option}')]`, time)
          /* Select option */
          .click(`//div[@id = '${selector_id}']//div[@class = 'multiselect__content-wrapper']//ul//li//span//span[contains(text(),'${option}')]`)
          .pause(1000)
          /* Press escape if necessary */
          .keys(browser.Keys.ESCAPE)
          .pause(500)
      }
    })
}

const createSubmission = (browser, obligation, period, party, edit_party = false, back_to_dashboard = false) => {
	logMessage(browser, 'Creating submission \'' + obligation + '\' for \'' + period + '\'')

  const submission = {
    obligation_selector: { option: obligation, read_write: true, singleSelectWithText: true },
    period_selector: { option: period, read_write: true, singleSelectWithText: false },
    party_selector: { option: party, read_write: edit_party, singleSelectWithText: true }
  }

  browser
    .useCss()
    .waitForElementVisible('.create-submission', 10000)

  for (const selector_id in submission) {
    if (submission[selector_id].read_write === true) {
      setMultiSelector(browser, selector_id, submission[selector_id].option, submission[selector_id].singleSelectWithText)
    }
  }

  browser
    .useXpath()
    .waitForElementVisible('//div[contains(@class,"create-submission")]//button', 5000)
    .click('//div[contains(@class,"create-submission")]//button')
    .pause(5000)
    .waitForElementVisible("//div[@class='toasted bulma success' and contains(text(), 'Submission added successfully.')]", 5000)

  if (back_to_dashboard === true) {
    browser.useXpath()
      .pause(500)
      .waitForElementVisible("//a[@href='/reporting/dashboard']", 10000)
      .click("//a[@href='/reporting/dashboard']")
      .pause(500)
  } else {
    browser.pause(5000)
  }
}

const handleModal = (browser, accept = true) => {
  const modal = "//div[@id='confirm-modal']"
  const acceptButton = "//button[contains(@class, 'btn-primary')]"
  const declineButton = "//button[contains(@class, 'btn-secondary')]"
  browser
    /* Check if moodal is opened */
    .useXpath()
    .waitForElementVisible(modal, 10000)
  if (accept) {
    browser
      .waitForElementVisible(modal + acceptButton, 10000)
      .click(modal + acceptButton)
  } else {
    browser
      .waitForElementVisible(modal + declineButton, 10000)
      .click(modal + declineButton)
  }
  browser
    .pause(500)
}

const deleteSubmissionFake = (browser) => {
	logMessage(browser, 'Fake delete')

  browser
    .useXpath()
    .waitForElementVisible("//button[@id='delete-button']", 10000)
    .click("//button[@id='delete-button']")
    .pause(500)
  handleModal(browser, false)
}
const deleteSubmission = (browser) => {
  browser
    .useXpath()
    .waitForElementVisible("//button[@id='delete-button']", 10000)
    .click("//button[@id='delete-button']")
    .pause(500)
  handleModal(browser)

  /* Validation */
  browser
    .waitForElementVisible("//div[@class='toasted bulma success' and contains(text(), 'Submission deleted')]", 5000)
    .waitForElementVisible("//table[@id='all-submissions-table']//div[contains(text(), 'There are no records to show')]", 10000)
}

const saveSubmission = (browser, tabs = []) => {
	logMessage(browser, 'Saving submission')

  browser.useXpath()
    /* Click Save and continue button */
    .execute('window.scrollTo(0,document.body.scrollHeight);')
    .waitForElementVisible("//footer[@class='app-footer']//button[@id='save-button']", 10000)
    .click("//footer[@class='app-footer']//button[@id='save-button']")
    .pause(500)
    .execute('document.body.scrollTop = 0;document.documentElement.scrollTop = 0')

  tabs.forEach(tab => {
    /* Check if desired tabs are valid */
    browser
      .waitForElementVisible(`//div[contains(@class,'form-wrapper')]//div[contains(@class, 'card-header')]//ul//li//div[contains(text(), '${tab}')]//i[contains(@class, 'fa-check-circle')]`, 20000)
  })
}

const selectTab = (browser, tab) => {
  browser
    .execute('window.scrollTo(0,0)')
    .useXpath()
    .waitForElementVisible(`//div[contains(@class, 'form-wrapper')]//div[contains(@class, 'card-header')]//ul//li//div[contains(text(), '${tab}')]`, 5000)
    .click(`//div[contains(@class, 'form-wrapper')]//div[contains(@class, 'card-header')]//ul//li//div[contains(text(), '${tab}')]`)
    .pause(1500)
}

const datePickerValue = (browser) => {
  const day = "//div[@id='date']//div[contains(@class, 'vdp-datepicker__calendar')][1]//span[contains(@class, 'cell day') and text()='1']"
  browser
    .waitForElementVisible("//div[@id='date']//input", 10000)
    .click("//div[@id='date']//input")
    .pause(1000)
    .waitForElementVisible(day, 10000)
    .click(day)
    .pause(1000)
}

const fillSubmissionInfo = (browser, submissionInfo = {}, autocomplet = true) => {
	logMessage(browser, 'Filling submission info')

  const fields = ['reporting_officer', 'designation', 'organization', 'postal_address', 'phone', 'email']
  /* Open Submission Info tab */
  selectTab(browser, 'Submission Info')
  browser.useXpath()
    .execute('window.scrollTo(0,document.body.scrollHeight);')
    .waitForElementVisible("//input[@id='reporting_officer']", 10000)
    .pause(500)

  fields.forEach(field => {
    /* Check if submissionInfo has missing fields */
    if (!submissionInfo.hasOwnProperty(field) && autocomplet) {
      submissionInfo[field] = ''
    } 

    if (submissionInfo.hasOwnProperty(field)) {
      /* Add submissionInfo in input fields */
      if (field === 'postal_address') {
        browser
          .setValue(`//textarea[@id='${field}']`, submissionInfo[field])
      } else {
        browser
          .setValue(`//input[@id='${field}']`, submissionInfo[field])
      }
    }
  })
  /* Add country name (special case) */
  if (submissionInfo.country !== undefined) {
    browser
      .waitForElementVisible("//form[@class='form-sections']//div[@class='multiselect']", 10000)
      .click("//form[@class='form-sections']//div[@class='multiselect']")
      .pause(500)
      .moveToElement(`//div[@id='country']//span[contains(text(),'${submissionInfo.country}')]`, 0, 0)
      .waitForElementVisible(`//div[@id='country']//span[contains(text(),'${submissionInfo.country}')]`, 10000)
      .pause(500)
      .click(`//div[@id='country']//span[contains(text(),'${submissionInfo.country}')]`)
      .pause(500)
  }
  /* Add date (special case) */
  datePickerValue(browser)
}

/**
 * 	saveAndFail(browser)
 *	Use this before calling clickQuestionnaireRadios(args)
 */
const saveAndFail = (browser, submissionInfo) => {
	logMessage(browser, 'Save and fail')

  fillSubmissionInfo(browser, submissionInfo)

  browser.useXpath()
    .execute('window.scrollTo(0,document.body.scrollHeight);')
    .waitForElementVisible("//footer[@class='app-footer']//button[@id='save-button']", 10000)
    .click("//footer[@class='app-footer']//button[@id='save-button']")
    .pause(500)
    .execute('document.body.scrollTop = 0;document.documentElement.scrollTop = 0')
    .waitForElementVisible("//div[contains(@class,'form-wrapper')]//div[contains(@class, 'card-header')]//ul//li//div[contains(text(), 'Submission Info')]//i[contains(@class, 'fa-times-circle')]", 20000)
}
/**
 * 	editSubmission(browser)
 *	Must be in dashboard before using this function
 */
const editSubmission = (browser, table_order) => {
  browser
    .useXpath()
    .waitForElementVisible(`//table[@id='data-entry-submissions-table']//tbody//tr[${table_order}]//span[contains(text(), 'Edit')]`, 10000)
    .click(`//table[@id='data-entry-submissions-table']//tbody//tr[${table_order}]//span[contains(text(), 'Edit')]`)
    .pause(3000)
}

const openLookupTable = (browser, page) => {
  browser
    .useCss()
    .execute('window.scrollTo(0,0)')
    .waitForElementVisible('li.router-link-exact-active', 20000)
    .moveToElement('li.router-link-exact-active', undefined, undefined, () => {
      browser
        .pause(500)
        .useXpath()
        .pause(500)
        .click(`//li[contains(@class, 'router-link-exact-active')]//a[contains(text(), '${page}')]`)
        .useCss()
        .moveToElement('.app-header h3', 0, 0)
        .pause(5000)
    })
}

const openDashboard = (browser) => {
  browser.useXpath()
    .waitForElementVisible("//a[@href='/reporting/dashboard']", 10000)
    .click("//a[@href='/reporting/dashboard']")
    .pause(3000)
    .waitForElementVisible('//div[@id="obligation_selector"]', 10000)
    .pause(3000)
    .assert.urlContains('/reporting/dashboard')
    .pause(3000)
}

const openGeneralInstructions = (browser) => {
  browser.useXpath()
    .waitForElementVisible("//button[contains(@class, 'btn-info-outline')]", 10000)
    .click("//button[contains(@class, 'btn-info-outline')]")
    .pause(500)
    .execute('window.scrollTo(0,0)')
    .pause(500)
    .click("//div[@id='instructions_modal']//header//button")
    .pause(500)
}

const openAsideMenu = (browser, tab) => {
  /* Toggler button */
  const aside_menu_toggler = `#${tab} .aside-menu .navbar-toggler-icon`
  /* Open aside menu if clossed */
  browser
    .execute('window.scrollTo(0,0)')
    .useXpath()
    .execute(function getContent(data) {
      /* Convert the unicode of toggler icon to string */
      return `\\u${getComputedStyle(document.querySelector(arguments[0]), ':before').content.replace(/'|"/g, '').charCodeAt(0).toString(16)}`
    }, [aside_menu_toggler], (result) => {
      const closed = '\\ue916'

      if (result.value === closed) {
        /* Open aside menu */
        browser
          .click(`//div[@id='${tab}']//aside[@class='aside-menu']//button[@class='navbar-toggler']`)
          .pause(1500)
      }
    })
}

const closeAsideMenu = (browser, tab) => {
  browser
    .execute('window.scrollTo(0,0)')
    .useXpath()
    .click(`//div[@id='${tab}']//aside[@class='aside-menu']//button[@class='navbar-toggler']`)
    .pause(500)
}

const filterSubmission = (browser, table, options, first_row_expected, rows_number_expected) => {
	logMessage(browser, 'Filtering submissions')

  const filters = {
    submission_search_filter: options[0],
    submission_obligation_filter: options[1],
    submission_party_filter: options[2],
    submission_from_filter: options[3],
    submission_to_filter: options[4]
  }
  const clear_button = 'submission_clear_button'

  browser
    .execute('window.scrollTo(0,document.body.scrollHeight);').pause(500)
    .useCss()
    .waitForElementVisible(`#${clear_button}`, 20000)
    .click(`#${clear_button}`)
    .pause(1000)

  for (const filter in filters) {
    if (filters[filter] !== '') {
      browser
        .element('css selector', `input#${filter}`, (result) => {
          if (result.status !== -1) {
            browser
              .useCss()
              .setValue(`#${filter}`, filters[filter])
              .pause(1000)
          } else {
            browser
              .useXpath()
              .moveTo(`//select[@id='${filter}']`, 0, 0)
              .pause(500)
              .click(`//select[@id='${filter}']`)
              .pause(500)
              .click(`//select[@id='${filter}']//option[contains(text(), '${filters[filter]}')]`)
              .pause(500)
              /* Press escape if necessary */
              .keys(browser.Keys.ESCAPE)
              .pause(500)
          }
        })
    }
  }

  browser.useXpath().execute('window.scrollTo(0,document.body.scrollHeight);').pause(500)

  first_row_expected.forEach((column_value, index) => {
    if (column_value !== '') {
      browser.waitForElementVisible(`//table[@id='${table}']//tbody//tr[1]//td[${index + 1}]//div[contains(text(), '${column_value}')]`, 20000)
    }
  })

  browser
    .elements('css selector', `#${table} tbody tr`, (result) => {
      browser.assert.equal(`${result.value.length} rows`, `${rows_number_expected} rows`)
    })
    .pause(500)
}

const filterEntity = (browser, tab, filters) => {
	logMessage(browser, 'Filtering entities')

  const tabs = {
    controlled_substances: {
      fields: ['substances-group-filter', 'substances-name-filter', 'substances-formula-filter'],
      clear: 'substances-clear-button'
    },
    blends: {
      fields: ['blends-name-filter', 'blends-component-filter'],
      clear: 'blends-clear-button'
    },
    parties: {
      fields: ['parties-name-filter'],
      clear: ''
    }
  }
  browser.execute('window.scrollTo(0,0)').useCss()
  tabs[tab].fields.forEach((field, index) => {
    browser
      .useCss()
      .element('css selector', `#${field} .multiselect__select`, (result) => {
        if (result.status !== -1) {
          browser
            .click(`#${field}`)
            .pause(500)
            .waitForElementVisible(`#${field} .multiselect__content-wrapper`, 5000)
            .useXpath()
            .click(`//div[@id='${field}']//div[@class='multiselect__content-wrapper']//ul//li//span//span[contains(text(),'${filters[index]}')]`)
            .pause(100)
            .keys(browser.Keys.ESCAPE)
            .pause(500)
        } else {
          browser
            .setValue(`input#${field}`, filters[index])
        }
      })
      .pause(1000)
  })
  browser.useCss().pause(2000)
  if (tabs[tab].clear !== '') {
    browser
      .waitForElementVisible(`#${tabs[tab].clear}`, 10000)
      .click(`#${tabs[tab].clear}`)
      .pause(1500)
  }
}

const checkSumbissionInfoFlags = (browser) => {
  const flags = [
    'flag_has_reported_a1', 'flag_has_reported_a2',
    'flag_has_reported_b1', 'flag_has_reported_b2', 'flag_has_reported_b3',
    'flag_has_reported_c1', 'flag_has_reported_c2', 'flag_has_reported_c3',
    'flag_has_reported_e',
    'flag_has_reported_f'
  ]
  /* Open Submission Info tab */
  selectTab(browser, 'Submission Info')
  /* Check all flags */
  flags.forEach(flag => {
    browser.useCss()
      .getAttribute(`#${flag}`, 'checked', (result) => {
        if (result.value !== 'true') {
          browser
            .useXpath()
            .waitForElementVisible(`(//label[@for='${flag}'])[2]`, 10000)
            .click(`(//label[@for='${flag}'])[2]`)
            .pause(500)
        }
      })
      .useCss()
      .expect.element(`#${flag}`).to.be.selected
  })
}

const clickQuestionnaireRadios = (browser, fields = [], allow_all = true) => {
	logMessage(browser, 'Clicking questionnaire radios: ' + fields)

  let restrictedFields = ['has_imports', 'has_exports', 'has_produced', 'has_destroyed', 'has_nonparty', 'has_emissions']
  const tabs = {
    has_imports: 'Imports',
    has_exports: 'Exports',
    has_produced: 'Production',
    has_destroyed: 'Destruction',
    has_nonparty: 'Nonparty',
    has_emission: 'Emission'
  }
  /* fields that will be set to 'yes' of no fields are given as argument */
  if (typeof fields !== 'undefined' && fields.length === 0 && allow_all === true) {
    fields = ['has_imports', 'has_exports', 'has_produced', 'has_destroyed', 'has_nonparty', 'has_emissions']
  }
  /* fields that will be set to 'no' */
  restrictedFields = restrictedFields.filter((e) => fields.indexOf(e) === -1)

  browser.useXpath()
  /* Check if all tabs are disabled */
  for (const tab in tabs) {
    browser
      .waitForElementVisible(`//div[contains(@class,'form-wrapper')]//div[contains(@class, 'card-header')]//a[contains(@class, 'disabled')]//div[contains(text(), '${tabs[tab]}')]`, 10000)
  }

  selectTab(browser, 'Questionnaire')

  browser
    .waitForElementVisible("//div[contains(@class, 'form-wrapper')]//div[contains(@class, 'card-header')]//a[not(contains(@class, 'disabled'))]//div[contains(text(), 'Questionnaire')]", 10000)
    .waitForElementVisible("//div[contains(@class, 'form-wrapper')]//div[contains(@class, 'card-header')]//a[not(contains(@class, 'disabled'))]//div[contains(text(), 'Files')]", 10000)
    .waitForElementVisible("//div[contains(@class, 'form-wrapper')]//div[contains(@class, 'card-header')]//a[not(contains(@class, 'disabled'))]//div[contains(text(), 'Submission Info')]", 10000)
    .waitForElementVisible("//div[contains(@class, 'form-wrapper')]//div[contains(@class, 'card-header')]//ul//li//div[contains(text(), 'Questionnaire')]", 10000)
    .useCss()
    .execute('window.scrollTo(0,250);')
    .waitForElementVisible('.field-wrapper #has_nonparty .custom-control:first-of-type label', 10000)
    .pause(500)
  /* Set fields to 'yes' */
  for (const field of fields) {
    browser
      .click(`.field-wrapper #${field} .custom-control:first-of-type label`)
  }
  /* Set restrictedFields to 'no' */
  for (const restrictedField of restrictedFields) {
    browser
      .click(`.field-wrapper #${restrictedField} .custom-control:nth-of-type(2) label`)
  }
}

const addEntity = (browser, tab, entity, options, order = undefined, check = false) => {
	logMessage(browser, 'Adding entity ' + entity + ': [\'' + options[0] + '\', \'' + options[1] + '\']')

  const selectors = []
  /**
   * 	Entity structure
   * 	entity: [tab_name, option_1_selector, option_2_selector, submit_button, table_id]
   * 	ex -> substance: ['Substance', 'FII', 'HFC-23', 'add-substance-button', 'fii-table']
   */
  const entities = {
    'substance': ['Substance', 'substance_annex_selector', 'substance_selector', 'add-substance-button', 'substance-table'],
    'blend': ['Blend', 'blend_type_selector', 'blend_selector', 'add-blend-button', 'blend-table']
  }
  /* Special case */
  // TODO: find a dynamic way
  if (options[0] === 'F') {
    entities.substance.pop()
    entities.substance.push('fii-table')
  }
  /* Correlate tabs with nav names and status column */
  const tabs_header = {
    has_imports_tab: { name: 'Imports', status_column: 9 },
    has_exports_tab: { name: 'Exports', status_column: 9 },
    has_produced_tab: { name: 'Production', status_column: 8 },
    has_destroyed_tab: { name: 'Destruction', status_column: 6 },
    has_nonparty_tab: { name: 'Nonparty', status_column: 10 }
  }
  /* Get XPath of aside menu components	*/
  const aside_menu = `//div[@id='${tab}']//aside[@class='aside-menu']`
  const aside_nav = `${aside_menu}//div[@class='tabs']//ul[@class='nav nav-tabs']`
  /* Get XPath of entity selectors	*/
  selectors.push(`${aside_menu}//div[@class='tabs']//div[@id='${entities[entity][1]}']`)
  selectors.push(`${aside_menu}//div[@class='tabs']//div[@id='${entities[entity][2]}']`)
  const add_entity_button = `${aside_menu}//div[@class='tabs']//button[@id='${entities[entity][3]}']`
  /* Open desired tab */
  selectTab(browser, tabs_header[tab].name)
  /* Open aside menu if clossed */
  openAsideMenu(browser, tab)
  browser
    .useXpath()
    /* Open entity form */
    .waitForElementVisible(`${aside_menu}//div[@class='tabs']`, 5000)
    .waitForElementVisible(`${aside_nav}//span[contains(text(), '${entities[entity][0]}')]`, 5000)
    .click(`${aside_nav}//span[contains(text(), '${entities[entity][0]}')]`)
    .pause(500)
  selectors.forEach((selector, index) => {
    browser
      /* Add option */
      .waitForElementVisible(selector, 5000)
      .click(selector)
      .pause(500)
      .waitForElementVisible(`${selector}//div[@class='multiselect__content-wrapper']`, 5000)
      .click(`${selector}//div[@class='multiselect__content-wrapper']//ul//li//span//span[text() = '${options[index]}']`)
      /* Close selector */
      .pause(100)
      .keys(browser.Keys.ESCAPE)
      .pause(500)
  })
  /* Submit entity */
  browser
    .waitForElementVisible(add_entity_button, 5000)
    .click(add_entity_button)
    .pause(500)

  closeAsideMenu(browser, tab)

  if (check === true) {
    browser
      /* Check if entity was added and status is invalid */
      .waitForElementVisible(`//div[@id='${tab}']//table[@id='${entities[entity][4]}']//tbody//tr[${order}]//td[${tabs_header[tab].status_column}]//span[contains(text(), 'invalid')]`, 5000)
      .moveTo(`//div[@id='${tab}']//table[@id='${entities[entity][4]}']//tbody//tr[${order}]//td[${tabs_header[tab].status_column}]`)

      .execute('document.getElementsByClassName(\'app-footer\')[0].style.display = \'none\'')
      .pause(500)

      .click(`//div[@id='${tab}']//table[@id='${entities[entity][4]}']//tbody//tr[${order}]//td[${tabs_header[tab].status_column}]//span[contains(text(), 'invalid')]`)
      .pause(500)

      .execute('document.getElementsByClassName(\'app-footer\')[0].style.display = \'inline\'')
      .pause(500)
      /* Check if Validation tab is opened and has a warrning */
      .waitForElementVisible(`${aside_menu}//div[@class='validation-tab']`, 5000)
      .waitForElementVisible(`${aside_nav}//span[contains(@class, 'badge-danger')]`, 5000)
      .execute('window.scrollTo(0,0)')

    closeAsideMenu(browser, tab)
  }
}

const addFacility = (browser, table, tab, row, row_values, start_column, check = false) => {
  /* Open desired tab */
  selectTab(browser, 'Emissions')
  browser
    .useCss()
    .execute('document.getElementsByClassName(\'app-footer\')[0].style.display = \'none\'')
    .pause(500)
    .click('#add-facility-button')

  if (check === true) {
    browser
      .useXpath()
      .click(`//div[@id='has_emissions_tab']//table[@id='facility-table']//tbody//tr[${row}]//td[11]//span[contains(text(), 'invalid')]`)
      .pause(500)

    closeAsideMenu(browser, 'has_emissions_tab')
  }

  /* Add values to facility */
  row_values.forEach((value, key) => {
    browser
      .useCss()
      .setValue(`#${tab} #${table} tbody tr:nth-child(${row}) td:nth-child(${key + start_column}) input`, value)
  })

  browser
    .pause(500)
    .execute('document.getElementsByClassName(\'app-footer\')[0].style.display = \'inline\'')
    .pause(500)
}

const addValues = (browser, table, tab, row, row_values, modal_values, start_column = 1) => {
	logMessage(browser, 'Adding values to entity')

  browser
    .useXpath()
    /* Hide app-footer	*/
    .execute('document.getElementsByClassName(\'app-footer\')[0].style.display = \'none\'')
    .pause(500)
    .useCss()
    .moveTo(`#${tab} #${table} tbody tr:nth-child(${row})`)
  /* Add values to entity */
  row_values.forEach((value, key) => {
    // TODO: find a way to add in textarea also
    browser
      .element('css selector', `#${tab} #${table} tbody tr:nth-child(${row}) td:nth-child(${key + start_column}) textarea`, (result) => {
        if (result.status !== -1) {
          browser
            .setValue(`#${tab} #${table} tbody tr:nth-child(${row}) td:nth-child(${key + start_column}) textarea`, value)
        } else {
          browser
            .setValue(`#${tab} #${table} tbody tr:nth-child(${row}) td:nth-child(${key + start_column}) input`, value)
        }
      })
  })
  /* Check if valid */
  browser
    .click(`#${tab} #${table}  tbody tr:nth-child(${row}) td:nth-child(2)`)
    .assert.containsText(`#${tab} #${table} .validation-wrapper > span`, 'valid')
  /* Open edit modal */
  browser.execute(`document.querySelector("#${tab} #${table} tbody tr:nth-child(${row})").classList.add("hovered")`, () => {
    browser
      .pause(500)
      .click(`#${tab} #${table} tbody tr:nth-child(${row}) td .row-controls span:not(.table-btn)`)
  })
  browser
    .waitForElementVisible(`#${tab} .modal-body`, 5000)
    .pause(500)
  /* Add values in modal */
  for (const field_id of Object.keys(modal_values)) {
    browser
      .click(`#${tab} .modal-body #${field_id}`)
      .pause(200)
      .clearValue(`#${tab} .modal-body #${field_id}`)
      .setValue(`#${tab} .modal-body #${field_id}`, modal_values[field_id])
  }
  /* Close modal */
  browser
    .pause(500)
    .click(`#${tab} .modal-dialog .close`)
    .pause(500)
    .execute(`document.querySelector("#${tab} #${table} tbody tr:nth-child(${row})").classList.remove("hovered")`, () => {})
    /* Show app-footer */
    .execute('document.getElementsByClassName(\'app-footer\')[0].style.display = \'inline\'')
    .pause(500)
}

const addComment = (browser, tab, comment) => {
	logMessage(browser, 'Adding comment')

  browser
    .useCss()
    .setValue(`#${tab} .comments-input textarea`, comment)
    .pause(500)
}

const rowIsEmpty = (browser, table, tab, row, row_values, modal_values, start_column = 1) => {
  browser
    .useXpath()
    /* Hide app-footer	*/
    .execute('document.getElementsByClassName(\'app-footer\')[0].style.display = \'none\'')
    .pause(500)
    .useCss()
    .moveTo(`#${tab} #${table} tbody tr:nth-child(${row})`)
  /* Check if row is empty */
  row_values.forEach((value, key) => {
    browser
      .element('css selector', `#${tab} #${table} tbody tr:nth-child(${row}) td:nth-child(${key + start_column}) textarea`, (result) => {
        if (result.status !== -1) {
          browser
            .getValue(`#${tab} #${table} tbody tr:nth-child(${row}) td:nth-child(${key + start_column}) textarea`, (data) => {
              browser.assert.equal(data.value, '')
            })
        } else {
          browser
            .getValue(`#${tab} #${table} tbody tr:nth-child(${row}) td:nth-child(${key + start_column}) input`, (data) => {
              browser.assert.equal(data.value, '')
            })
        }
      })
  })
  /* Open edit modal */
  browser.execute(`document.querySelector("#${tab} #${table} tbody tr:nth-child(${row})").classList.add("hovered")`, () => {
    browser
      .pause(500)
      .click(`#${tab} #${table} tbody tr:nth-child(${row}) td .row-controls span:not(.table-btn)`)
  })
  browser
    .waitForElementVisible(`#${tab} .modal-body`, 5000)
    .pause(500)
  /* Check if modal inputs are empty */
  for (const field_id of Object.keys(modal_values)) {
    browser
      .getValue(`#${tab} .modal-body #${field_id}`, (data) => {
        browser.assert.equal(data.value, '')
      })
  }
  /* Close modal */
  browser
    .pause(500)
    .click(`#${tab} .modal-dialog .close`)
    .pause(500)
    .execute(`document.querySelector("#${tab} #${table} tbody tr:nth-child(${row})").classList.remove("hovered")`, () => {})
    /* Show app-footer */
    .execute('document.getElementsByClassName(\'app-footer\')[0].style.display = \'inline\'')
    .pause(500)
}

const uploadeFile = (browser, filename, filepath) => {
	logMessage(browser, 'Uploading file')

  const path = require('path')
  const find_root = require('find-root')
  const root = find_root(path.resolve(__dirname))
  const file = path.resolve(root + filename + filepath)
  console.log(file)
  browser
    .useCss()
    .waitForElementVisible('#choose-files-button__BV_file_outer_', 10000)
    .setValue('input#choose-files-button', file, (result) => {
      if (result.status !== 0) {
        console.log(result)
      }
    })
    .pause(1000)
}

module.exports = {
  login,
  logout,
  setMultiSelector,
  createSubmission,
  deleteSubmissionFake,
  deleteSubmission,
  saveSubmission,
  saveAndFail,
  editSubmission,
  selectTab,
  openLookupTable,
  openDashboard,
  openGeneralInstructions,
  openAsideMenu,
  closeAsideMenu,
  filterSubmission,
  filterEntity,
  fillSubmissionInfo,
  checkSumbissionInfoFlags,
  clickQuestionnaireRadios,
  addEntity,
  addFacility,
  addValues,
  addComment,
  rowIsEmpty,
  uploadeFile
}
