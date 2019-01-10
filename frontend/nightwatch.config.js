module.exports = {
	test_settings: {
		default: {
			desiredCapabilities: {
				browserName: 'chrome',
				chromeOptions: {
					args: [
						'--headless',
						'--no-sandbox',
						'--disable-dev-shm-usage',
					]
				},
				acceptSslCerts: true
			}
		}
	}
}
