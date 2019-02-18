const login = (browser, username, password) => {
	browser.url(process.env.VUE_DEV_SERVER_URL)
		.useCss()
		.waitForElementVisible('#id_username', 20000)
		.setValue('#id_username', username)
		.setValue('#id_password', password)
		.waitForElementVisible('button[type="submit"]', 10000)
		.pause(1000)
		.click('button[type="submit"]')
		.waitForElementVisible('h3', 8000)
		.assert.urlContains('/reporting/dashboard')
}

const logout = (browser) => {
	browser.useCss()
		.waitForElementVisible('#account_options', 5000)
		.click('#account_options')
		.waitForElementVisible('#logout_button', 5000)
		.click('#logout_button')
		.waitForElementVisible('#id_username', 5000)
		.assert.urlContains('/admin/login')
}

const createSubmission = (browser, obligation, period) => {
	browser.useCss()
		.waitForElementVisible('.create-submission', 10000)
		.waitForElementVisible('#obligation_selector', 10000)
		.waitForElementVisible('#obligation_selector .multiselect', 10000)
		.click('#obligation_selector .multiselect')
		.waitForElementVisible('#obligation_selector .multiselect__content-wrapper', 10000)
		.useXpath()
		.waitForElementVisible(`//span[contains(text(),'${obligation}')]/ancestor::div[contains(@id, 'obligation_selector')]`, 5000)
		.click(`//div[@id="obligation_selector"]//ul//li//span//span[contains(text(),'${obligation}')]`)
		.useCss()
		.waitForElementVisible('#period_selector', 2000)
		.waitForElementVisible('#period_selector .multiselect', 2000)
		.pause(500)
		.click('#period_selector .multiselect')
		.pause(500)
		.waitForElementVisible('#period_selector .multiselect__content-wrapper', 2000)
		.useXpath()
		.waitForElementVisible(`//span[contains(text(),'${period}')]/ancestor::div[contains(@id, 'period_selector')]`, 5000)
		.click(`//div[@id="period_selector"]//ul//li//span//span[contains(text(),'${period}')]`)
		.waitForElementVisible('//div[contains(@class,"create-submission")]//button', 5000)
		.click('//div[contains(@class,"create-submission")]//button')
		.pause(5000)
		.waitForElementVisible("//div[@class='toasted bulma success' and contains(text(), 'Submission created')]", 5000)
		.pause(5000)
}

const deleteSubmission = (browser) => {
	browser.useXpath()
		/* Fake delete */
		.waitForElementVisible("//button[@id='delete-button']", 10000)
		.click("//button[@id='delete-button']")
		.pause(500)
		.dismissAlert()
		/* Delete Submission */
		.waitForElementVisible("//button[@id='delete-button']", 10000)
		.click("//button[@id='delete-button']")
		.pause(500)
		.acceptAlert()
		.waitForElementVisible("//div[@class='toasted bulma success' and contains(text(), 'Submission deleted')]", 5000)
		.waitForElementVisible("//table[@id='all-submissions-table']//div[contains(text(), 'There are no records to show')]", 10000)
}

const saveSubmission = (browser, tabs = []) => {
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

const fillSubmissionInfo = (browser, submissionInfo = {}) => {
	const fields = ['reporting_officer', 'designation', 'organization', 'postal_address', 'phone', 'email', 'date']
	/* Open Submission Info tab */
	selectTab(browser, 'Submission Info')
	browser.useXpath()
		.execute('window.scrollTo(0,document.body.scrollHeight);')
		.waitForElementVisible("//input[@id='reporting_officer']", 10000)
		.pause(500)

	fields.forEach(field => {
		/* Check if submissionInfo has missing fields */
		if (!submissionInfo.hasOwnProperty(field)) {
			submissionInfo[field] = ''
		}
		/* Add submissionInfo in input fields */
		if (field === 'postal_address') {
			browser
				.setValue(`//textarea[@id='${field}']`, submissionInfo[field])
		} else {
			browser
				.setValue(`//input[@id='${field}']`, submissionInfo[field])
		}
	})
	/* Add country name (special case) */
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

/**
 * 	saveAndFail(browser)
 *	Use this before calling clickQuestionnaireRadios(args)
 */
const saveAndFail = (browser) => {
	const submissionInfo = {
		reporting_officer: 'test name',
		designation: 'test designation',
		organization: 'test organisation',
		postal_address: 'test address',
		country: 'France',
		phone: '+490000000',
		email: 'john.doe@gmail.com',
		date: '01/11/2019'
	}

	fillSubmissionInfo(browser, submissionInfo)

	browser.useXpath()
		.execute('window.scrollTo(0,document.body.scrollHeight);')
		.waitForElementVisible("//footer[@class='app-footer']//button[@id='save-button']", 10000)
		.click("//footer[@class='app-footer']//button[@id='save-button']")
		.pause(500)
		.execute('document.body.scrollTop = 0;document.documentElement.scrollTop = 0')
		.waitForElementVisible("//div[contains(@class,'form-wrapper')]//div[contains(@class, 'card-header')]//ul//li//div[contains(text(), 'Questionnaire')]//i[contains(@class, 'fa-times-circle')]", 20000)
}
/**
 * 	editSubmission(browser)
 *	Must be in dashboard before using this function
 */
const editSubmission = (browser, table_order) => {
	browser.useXpath()
		.waitForElementVisible(`//table[@id='data-entry-submissions-table']//tbody//tr[${table_order}]//span[contains(text(), 'Continue')]`, 10000)
		.click(`//table[@id='data-entry-submissions-table']//tbody//tr[${table_order}]//span[contains(text(), 'Continue')]`)
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

const filterEntity = (browser, tab, filters) => {
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
		'flag_provisional',
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

	browser
		.waitForElementVisible("//div[contains(@class, 'form-wrapper')]//div[contains(@class, 'card-header')]//a[not(contains(@class, 'disabled'))]//div[contains(text(), 'Questionnaire')]", 10000)
		.waitForElementVisible("//div[contains(@class, 'form-wrapper')]//div[contains(@class, 'card-header')]//a[not(contains(@class, 'disabled'))]//div[contains(text(), 'Files')]", 10000)
		.waitForElementVisible("//div[contains(@class, 'form-wrapper')]//div[contains(@class, 'card-header')]//a[not(contains(@class, 'disabled'))]//div[contains(text(), 'Submission Info')]", 10000)
		.waitForElementVisible("//div[contains(@class, 'form-wrapper')]//div[contains(@class, 'card-header')]//ul//li//div[contains(text(), 'Questionnaire')]", 10000)
		.click("//div[contains(@class,'form-wrapper')]//div[contains(@class, 'card-header')]//ul//li//div[contains(text(), 'Questionnaire')]")
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
	if (options[0] === 'FII') {
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
			.click(`${selector}//div[@class='multiselect__content-wrapper']//ul//li//span//span[contains(text(),'${options[index]}')]`)
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
			.setValue(`#${tab} #${table} tbody tr:nth-child(${row}) td:nth-child(${key + start_column}) input`, value)
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
	for (const value of Object.keys(modal_values)) {
		browser
			.click(`#${tab} .modal-body #${value}`)
			.pause(200)
			.clearValue(`#${tab} .modal-body #${value}`)
			.setValue(`#${tab} .modal-body #${value}`, modal_values[value])
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
	browser
		.useCss()
		.setValue(`#${tab} .comments-input textarea`, comment)
		.pause(500)
}

const uploadeFile = (browser, filename, filepath) => {
	const path = require('path')
	const find_root = require('find-root')
	const root = find_root(path.resolve(__dirname))
	const file = path.resolve(root + filename + filepath)

	browser
		.useCss()
		.waitForElementVisible('#choose-files-button', 10000)
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
	createSubmission,
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
	filterEntity,
	fillSubmissionInfo,
	checkSumbissionInfoFlags,
	clickQuestionnaireRadios,
	addEntity,
	addFacility,
	addValues,
	addComment,
	uploadeFile
}
