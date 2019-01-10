module.exports = {
	test_settings: {
		default: {
			desiredCapabilities: {
				browserName: 'chrome',
				chromeOptions: {
					args: [
						'--headless'
					]
				},
				acceptSslCerts: true
			}
		}
	}
}
