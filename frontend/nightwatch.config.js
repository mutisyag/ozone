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
						'--window-size=1800,900'
					]
				},
				acceptSslCerts: true
			}
		}
	}
}
