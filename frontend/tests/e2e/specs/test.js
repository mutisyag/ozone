/* eslint-disable func-style */
/* eslint-disable no-unused-vars */
// For authoring Nightwatch tests, see
// http://nightwatchjs.org/guide#usage

// or more concisely

const util = require('util')
const execSync = util.promisify(require('child_process').execSync)
// const getSelectElementByContent = require('../custom-assertions/customSelectors')

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
		browser
			.url(process.env.VUE_DEV_SERVER_URL)
			// start login
			.waitForElementVisible('#id_username', 20000)
			.setValue('#id_username', 'party')
			.setValue('#id_password', 'party')
			.waitForElementVisible('button[type="submit"]', 10000)
			.pause(1000)
			.click('button[type="submit"]')
			.waitForElementVisible('h3', 8000)
			.assert.urlContains('/reporting/dashboard')
		// end login
		// start create submission
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
			.click('#period_selector .multiselect')
			.waitForElementVisible('#period_selector .multiselect__content-wrapper', 2000)
			.useXpath()
			.waitForElementVisible("//span[contains(text(),'2018')]/ancestor::div[contains(@id, 'period_selector')]", 5000)
			.click('//div[@id="period_selector"]//ul//li//span//span[contains(text(),"2018")]')
			.waitForElementVisible('//div[contains(@class,"create-submission")]//button', 5000)
			.click('//div[contains(@class,"create-submission")]//button')
		// end create submission
			.end()
	}
}
