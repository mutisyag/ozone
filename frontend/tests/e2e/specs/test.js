/* eslint-disable func-style */
/* eslint-disable no-unused-vars */
// For authoring Nightwatch tests, see
// http://nightwatchjs.org/guide#usage

// or more concisely
const util = require('util')
const execSync = util.promisify(require('child_process').execSync)

module.exports = {
	before: () => {
		console.log('running backend')
		execSync('bash ../utility/setup_backend.sh', { env: process.env })
		console.log('done running backend')
	},
	after: () => {
		console.log('running cleanup')
		execSync('bash ../utility/cleanup_backend.sh', { env: process.env })
		console.log('done running cleanup')
	},
	'default e2e tests': browser => {
		browser
			.url(process.env.VUE_DEV_SERVER_URL)
			.waitForElementVisible('.app', 8000)
			.assert.elementPresent('.app-header')
			.assert.containsText('h3', 'ORS (Ozone online reporting system)')
			.assert.elementCount('h3', 1)
			.end()
	}
}
