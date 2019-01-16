const login = (browser, username, password) => {
	browser.url(process.env.VUE_DEV_SERVER_URL)
	// start login
		.waitForElementVisible('#id_username', 20000)
		.setValue('#id_username', username)
		.setValue('#id_password', password)
		.waitForElementVisible('button[type="submit"]', 10000)
		.pause(1000)
		.click('button[type="submit"]')
		.waitForElementVisible('h3', 8000)
		.assert.urlContains('/reporting/dashboard')
}

const createSubmission = (browser) => {
	browser.waitForElementVisible('.create-submission', 10000)
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
}

const clickQuestionnaireRadios = (browser) => {
	browser
		.waitForElementVisible('//div[contains(@class,"form-wrapper")]//div[contains(@class, "card-header")]//ul//li//div[contains(text(), "Questionnaire")]', 10000)
		.click('//div[contains(@class,"form-wrapper")]//div[contains(@class, "card-header")]//ul//li//div[contains(text(), "Questionnaire")]')
		.useCss()
		.execute('window.scrollTo(0,document.body.scrollHeight);')
		.waitForElementVisible('.field-wrapper #has_emissions .custom-control:first-of-type label', 10000)
		.pause(500)
	for (const field of ['#has_imports', '#has_exports', '#has_produced', '#has_destroyed', '#has_nonparty', '#has_emissions']) {
		browser
			.click(`.field-wrapper ${field} .custom-control:first-of-type label`)
	}
}

const selectTab = (browser, tab) => {
	browser
		.execute('window.scrollTo(0,0)')
		.useXpath()
		.click(`//div[contains(@class,"form-wrapper")]//div[contains(@class, "card-header")]//ul//li//div[contains(text(), '${tab}')]`)
		.useCss()
		.waitForElementVisible('.aside-menu', 10000)
}

const addSubstance = (browser, select_id, option) => {
	browser
		.click('.aside-menu .tabs .nav-tabs li a')
		.click(`#${select_id} .multiselect`)
		.waitForElementVisible(`#${select_id} .multiselect__content-wrapper`, 10000)
		.useXpath()
		.waitForElementVisible(`//span[contains(text(),'${option}')]/ancestor::div[contains(@id, '${select_id}')]`, 5000)
		.click(`//div[@id='${select_id}']//ul//li//span//span[contains(text(),'${option}')]`)
		.keys(browser.Keys.ESCAPE)
		.useCss()
		.click('#add-substance-button')
		.moveToElement('aside.aside-menu > div > .navbar-toggler', undefined, undefined)
		.pause(500)
		.click('aside.aside-menu > div > .navbar-toggler')
}

const addBlend = (browser, select_id, option) => {
	browser
		.waitForElementVisible('.aside-menu .navbar-toggler', 10000)
		.moveToElement('aside.aside-menu > div > .navbar-toggler', undefined, undefined)
		.pause(500)
		.click('#has_imports_tab aside.aside-menu > div > .navbar-toggler')
		.pause(500)
		.waitForElementVisible('#has_imports_tab .aside-menu .tabs .nav-tabs li:nth-child(2)', 10000)
		.click('#has_imports_tab .aside-menu .tabs .nav-tabs li:nth-child(2) a')
		.pause(500)
		.click(`#${select_id} .multiselect`)
		.pause(500)
		.waitForElementVisible(`#${select_id} .multiselect__content-wrapper`, 10000)
		.useXpath()
		.waitForElementVisible(`//span[contains(text(),'${option}')]/ancestor::div[contains(@id, '${select_id}')]`, 5000)
		.click(`//div[@id='${select_id}']//ul//li//span//span[contains(text(),'${option}')]`)
		.keys(browser.Keys.ESCAPE)
		.useCss()
		.waitForElementVisible('#add-blend-button', 5000)
		.pause(500)
		.click('#add-blend-button')
		.moveToElement('aside.aside-menu > div > .navbar-toggler', undefined, undefined)
		.pause(500)
		.click('aside.aside-menu > div > .navbar-toggler')
}

const addValues = (browser, table, tab) => {
	browser
		.setValue(`${table} tbody tr td:nth-child(4) input`, 100)
		.setValue(`${table} tbody tr td:nth-child(5) input`, 5)
		.click(`${table}  tbody tr td:nth-child(2)`)
		.assert.containsText(`${table} .validation-wrapper > span`, 'valid')
	browser.execute(`document.querySelector("${table} tbody tr").classList.add("hovered")`, () => {
		browser
			.pause(5000)
			.click(`${table} tbody tr td .row-controls span:not(.table-btn)`)
	})
	browser
		.waitForElementVisible(`${tab} .modal-body`, 5000)
		.pause(500)
		.setValue(`${tab} .modal-body #quantity_feedstock`, 1)
		.setValue(`${tab} .modal-body #quantity_critical_uses`, 1)
		.setValue(`${tab} .modal-body #decision_critical_uses`, 'asd')
		.pause(5000)
		.click(`${tab} .modal-dialog .close`)
		.pause(500)
}

module.exports = {
	login,
	createSubmission,
	clickQuestionnaireRadios,
	selectTab,
	addSubstance,
	addBlend,
	addValues
}
