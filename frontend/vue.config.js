module.exports = {
	chainWebpack: config => {
		config.output.chunkFilename('js/[name].[id].[chunkhash:8].js')
	}
}
