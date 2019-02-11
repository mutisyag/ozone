const login = (browser, username, password) => {
	browser.url(process.env.VUE_DEV_SERVER_URL)
	// start login
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

const createSubmission = (browser) => {
	browser.useCss()
		.waitForElementVisible('.create-submission', 10000)
		.waitForElementVisible('#obligation_selector', 10000)
		.waitForElementVisible('#obligation_selector .multiselect', 10000)
		.click('#obligation_selector .multiselect')
		.waitForElementVisible('#obligation_selector .multiselect__content-wrapper', 10000)
		.useXpath()
		.waitForElementVisible("//span[contains(text(),'Article 7')]/ancestor::div[contains(@id, 'obligation_selector')]", 5000)
		.click('//div[@id="obligation_selector"]//ul//li//span//span[contains(text(),"Article 7")]')
		.useCss()
		.waitForElementVisible('#period_selector', 2000)
		.waitForElementVisible('#period_selector .multiselect', 2000)
		.pause(500)
		.click('#period_selector .multiselect')
		.pause(500)
		.waitForElementVisible('#period_selector .multiselect__content-wrapper', 2000)
		.useXpath()
		.waitForElementVisible("//span[contains(text(),'2018')]/ancestor::div[contains(@id, 'period_selector')]", 5000)
		.click('//div[@id="period_selector"]//ul//li//span//span[contains(text(),"2018")]')
		.waitForElementVisible('//div[contains(@class,"create-submission")]//button', 5000)
		.click('//div[contains(@class,"create-submission")]//button')
		.waitForElementVisible("//div[@class='toasted bulma success' and contains(text(), 'Submission created')]", 5000)
}

const deleteSubmission = (browser) => {
	browser.useXpath()
		//	Fake delete
		.waitForElementVisible("//button[@id='delete-button']", 10000)
		.click("//button[@id='delete-button']")
		.pause(500)
		.dismissAlert()
		//	Delete Submission
		.waitForElementVisible("//button[@id='delete-button']", 10000)
		.click("//button[@id='delete-button']")
		.pause(500)
		.acceptAlert()
		.waitForElementVisible("//div[@class='toasted bulma success' and contains(text(), 'Submission deleted')]", 5000)
		.waitForElementVisible("//table[@id='all-submissions-table']//div[contains(text(), 'There are no records to show')]", 10000)
}

const saveSubmission = (browser) => {
	browser.useXpath()
		.waitForElementVisible("//footer[@class='app-footer']//button[@id='save-button']", 10000)
		.click("//footer[@class='app-footer']//button[@id='save-button']")
		.pause(500)
		.execute('document.body.scrollTop = 0;document.documentElement.scrollTop = 0')
		.waitForElementVisible("//div[contains(@class,'form-wrapper')]//div[contains(@class, 'card-header')]//ul//li//div[contains(text(), 'Questionnaire')]//i[contains(@class, 'fa-check-circle')]", 20000)
}
/**
 * 	saveAndFail(browser)
 *	Use this before calling clickQuestionnaireRadios(args)
 */
const saveAndFail = (browser) => {
	browser.useXpath()
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
const editSubmission = (browser) => {
	browser.useXpath()
		.waitForElementVisible("//table[@id='data-entry-submissions-table']//tbody//tr[1]//span[contains(text(), 'Continue')]", 10000)
		.click("//table[@id='data-entry-submissions-table']//tbody//tr[1]//span[contains(text(), 'Continue')]")
		.pause(500)
}

const openDashboard = (browser) => {
	browser.useXpath()
		.waitForElementVisible("//a[@href='/reporting/dashboard']", 10000)
		.click("//a[@href='/reporting/dashboard']")
		.pause(500)
		.assert.urlContains('/reporting/dashboard')
}

const fillSubmissionInfo = (browser, submissionInfo = {}) => {
	browser.useXpath()
		.waitForElementVisible('//div[contains(@class,"form-wrapper")]//div[contains(@class, "card-header")]//ul//li//div[contains(text(), "Submission Info")]', 10000)
		.click("//div[contains(@class,'form-wrapper')]//div[contains(@class, 'card-header')]//ul//li//div[contains(text(), 'Submission Info')]")
		.pause(500)
		.execute('window.scrollTo(0,document.body.scrollHeight);')
		.waitForElementVisible("//input[@id='reporting_officer']", 10000)
		.pause

	const fields = ['reporting_officer', 'designation', 'organization', 'postal_code', 'phone', 'fax', 'email', 'date']
	const flags = [
		'flag_provisional',
		'flag_has_reported_a1', 'flag_has_reported_a2',
		'flag_has_reported_b1', 'flag_has_reported_b2', 'flag_has_reported_b3',
		'flag_has_reported_c1', 'flag_has_reported_c2', 'flag_has_reported_c3',
		'flag_has_reported_e',
		'flag_has_reported_f'
	]

	fields.forEach(field => {
		/* Check if submissionInfo has missing fields */
		if (!submissionInfo.hasOwnProperty(field)) {
			submissionInfo[field] = ''
		}
		browser
			.setValue(`//input[@id='${field}']`, submissionInfo[field])
	})

	browser
		.waitForElementVisible("//form[@class='form-sections']//div[@class='multiselect']", 10000)
		.click("//form[@class='form-sections']//div[@class='multiselect']")
		.pause(500)
		.moveToElement(`//div[@id='country']//span[contains(text(),'${submissionInfo.country}')]`, 0, 0)
		.waitForElementVisible(`//div[@id='country']//span[contains(text(),'${submissionInfo.country}')]`, 10000)
		.pause(500)
		.click(`//div[@id='country']//span[contains(text(),'${submissionInfo.country}')]`)

	flags.forEach(flag => {
		browser.useCss()
			.getAttribute(`#${flag}`, 'checked', (result) => {
				if (result.value != 'true') {
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
	let restrictedFields = ['#has_imports', '#has_exports', '#has_produced', '#has_destroyed', '#has_nonparty', '#has_emissions']

	if (typeof fields !== 'undefined' && fields.length == 0 && allow_all === true) {
		fields = ['#has_imports', '#has_exports', '#has_produced', '#has_destroyed', '#has_nonparty', '#has_emissions']
	}

	restrictedFields = restrictedFields.filter((e) => fields.indexOf(e) === -1)

	browser.useXpath()
		.waitForElementVisible("//div[contains(@class,'form-wrapper')]//div[contains(@class, 'card-header')]//a[contains(@class, 'disabled')]//div[contains(text(), 'Imports')]", 5000)
		.waitForElementVisible("//div[contains(@class,'form-wrapper')]//div[contains(@class, 'card-header')]//a[contains(@class, 'disabled')]//div[contains(text(), 'Exports')]", 5000)
		.waitForElementVisible("//div[contains(@class,'form-wrapper')]//div[contains(@class, 'card-header')]//a[contains(@class, 'disabled')]//div[contains(text(), 'Production')]", 5000)
		.waitForElementVisible("//div[contains(@class,'form-wrapper')]//div[contains(@class, 'card-header')]//a[contains(@class, 'disabled')]//div[contains(text(), 'Destruction')]", 5000)
		.waitForElementVisible("//div[contains(@class,'form-wrapper')]//div[contains(@class, 'card-header')]//a[contains(@class, 'disabled')]//div[contains(text(), 'Nonparty')]", 5000)
		.waitForElementVisible("//div[contains(@class,'form-wrapper')]//div[contains(@class, 'card-header')]//a[contains(@class, 'disabled')]//div[contains(text(), 'Emissions')]", 5000)
		.waitForElementVisible("//div[contains(@class,'form-wrapper')]//div[contains(@class, 'card-header')]//a[not(contains(@class, 'disabled'))]//div[contains(text(), 'Questionnaire')]", 5000)
		.waitForElementVisible("//div[contains(@class,'form-wrapper')]//div[contains(@class, 'card-header')]//a[not(contains(@class, 'disabled'))]//div[contains(text(), 'Files')]", 5000)
		.waitForElementVisible("//div[contains(@class,'form-wrapper')]//div[contains(@class, 'card-header')]//a[not(contains(@class, 'disabled'))]//div[contains(text(), 'Submission Info')]", 5000)

		.waitForElementVisible('//div[contains(@class,"form-wrapper")]//div[contains(@class, "card-header")]//ul//li//div[contains(text(), "Questionnaire")]', 10000)
		.click('//div[contains(@class,"form-wrapper")]//div[contains(@class, "card-header")]//ul//li//div[contains(text(), "Questionnaire")]')
		.useCss()
		.execute('window.scrollTo(0,document.body.scrollHeight);')
		.waitForElementVisible('.field-wrapper #has_emissions .custom-control:first-of-type label', 10000)
		.pause(500)

	for (const field of fields) {
		browser
			.click(`.field-wrapper ${field} .custom-control:first-of-type label`)
	}

	for (const restrictedField of restrictedFields) {
		browser
			.click(`.field-wrapper ${restrictedField} .custom-control:nth-of-type(2) label`)
	}
}

const selectTab = (browser, tab_title) => {
	browser
		.execute('window.scrollTo(0,0)')
		.useXpath()
		.click(`//div[contains(@class,"form-wrapper")]//div[contains(@class, "card-header")]//ul//li//div[contains(text(), '${tab_title}')]`)
}

const addEntity = (browser, tab, entities_type, selector_id, option) => {
	const aside_menu = `//div[@id='${tab}']//aside[@class='aside-menu']`
	const aside_nav = `${aside_menu}//div[@class='tabs']//ul[@class='nav nav-tabs']`
	const entities_selector = `${aside_menu}//div[@class='tabs']//div[@id='${selector_id}']`
	const selector = `#${tab} .aside-menu .navbar-toggler-icon`
	let add_button = `${aside_menu}//div[@class='tabs']`

	if (entities_type === 'Substances') {
		add_button += '//button[@id=\'add-substance-button\']'
	} else {
		add_button += '//button[@id=\'add-blend-button\']'
	}

	browser
		.useXpath()
		.execute(function getContent(data) {
			/** Convert the unicode of toggler icon to string * */
			return `\\u${getComputedStyle(document.querySelector(arguments[0]), ':before').content.replace(/'|"/g, '').charCodeAt(0).toString(16)}`
		}, [selector], (result) => {
			const closed = '\\ue916'

			if (result.value == closed) {
				/** Open aside menu * */
				browser
					.click(`${aside_menu}//button[@class='navbar-toggler']`)
					.pause(1500)
					.waitForElementVisible(`${aside_nav}//span[contains(text(), '${entities_type}')]`, 5000)
			}
		})

	browser
		.useXpath()
		.waitForElementVisible(`${aside_menu}//div[@class='tabs']`, 5000)
		.click(`${aside_nav}//span[contains(text(), '${entities_type}')]`)
		.pause(500)
		.waitForElementVisible(entities_selector, 5000)
		.click(entities_selector)
		.pause(500)
		.waitForElementVisible(`${entities_selector}//div[@class='multiselect__content-wrapper']`, 5000)
		.click(`${entities_selector}//div[@class='multiselect__content-wrapper']//ul//li//span//span[contains(text(),'${option}')]`)
		.pause(500)
		.keys(browser.Keys.ESCAPE)
		.waitForElementVisible(add_button, 5000)
		.click(add_button)
		.pause(500)
		/* Close aside menu  */
		.click(`${aside_menu}//button[@class='navbar-toggler']`)
		.pause(500)
}

const addValues = (browser, table, tab) => {
	browser
		.useCss()
		.setValue(`${table} tbody tr td:nth-child(4) input`, 100)
		.setValue(`${table} tbody tr td:nth-child(5) input`, 5)
		.click(`${table}  tbody tr td:nth-child(2)`)
		.assert.containsText(`${table} .validation-wrapper > span`, 'valid')
	browser.execute(`document.querySelector("${table} tbody tr").classList.add("hovered")`, () => {
		browser
			.pause(500)
			.click(`${table} tbody tr td .row-controls span:not(.table-btn)`)
	})
	browser
		.waitForElementVisible(`${tab} .modal-body`, 5000)
		.pause(500)
		.setValue(`${tab} .modal-body #quantity_feedstock`, 1)
		.setValue(`${tab} .modal-body #quantity_critical_uses`, 1)
		.setValue(`${tab} .modal-body #decision_critical_uses`, 'asd')
		.pause(500)
		.click(`${tab} .modal-dialog .close`)
		.pause(500)
}

module.exports = {
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
	addValues
}
