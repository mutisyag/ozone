// http://nightwatchjs.org/gettingstarted#settings-file

const deepmerge = require('deepmerge')
const userOptions = JSON.parse(process.env.VUE_NIGHTWATCH_USER_OPTIONS || '{}')

module.exports = deepmerge({
  src_folders: ['tests/e2e/specs'],
  output_folder: 'tests/e2e/reports',
  custom_assertions_path: ['tests/e2e/custom-assertions'],

  selenium: {
    start_process: true,
    server_path: '/usr/local/lib/node_modules/webdriver-manager/selenium/selenium-server-standalone-3.141.59.jar',
    host: '127.0.0.1',
    port: 4444,
    cli_args: {
      'webdriver.chrome.driver': '/usr/local/lib/node_modules/webdriver-manager/selenium/chromedriver_76.0.3809.12'
    }
  },

  test_settings: {
    default: {
      selenium_port: 4444,
      selenium_host: 'localhost',
      silent: true
    },

    chrome: {
      desiredCapabilities: {
        browserName: 'chrome',
        javascriptEnabled: true,
        acceptSslCerts: true
      }
    }
  }
}, userOptions)
