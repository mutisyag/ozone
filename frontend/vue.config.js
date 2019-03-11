const path = require('path')

module.exports = {
	chainWebpack: config => {
		if (process.env.NODE_ENV !== 'production') {
			config.devtool('eval')
			config.module
				.rule('istanbul')
				.test(/\.(js|vue)$/)
				.enforce('post')
				.include
				.add(path.resolve(__dirname, '/src'))
				.end()
				.use('istanbul-instrumenter-loader')
				.loader('istanbul-instrumenter-loader')
				.options({ esModules: true })
		}
	}
}
