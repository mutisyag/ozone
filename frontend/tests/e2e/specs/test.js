/* eslint-disable func-style */
/* eslint-disable no-unused-vars */
// For authoring Nightwatch tests, see
// http://nightwatchjs.org/guide#usage

// or more concisely
const sys = require('sys')
const { exec } = require('child_process')

module.exports = {
	before: (browser) => {
		console.log('Setting up...')
		function puts(error, stdout, stderr) { sys.puts(stdout) }
		exec('ls -la', puts)
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
