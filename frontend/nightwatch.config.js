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
						'--window-size=1300,850'
					]
				},
				acceptSslCerts: true
			}
		}
	}
}
