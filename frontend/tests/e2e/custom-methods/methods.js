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
		.click('#period_selector .multiselect')
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

module.exports = {
	login,
	createSubmission,
	clickQuestionnaireRadios,
	selectTab
}
