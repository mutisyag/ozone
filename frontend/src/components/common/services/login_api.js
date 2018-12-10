import {
	post, api, getCookie, remove
} from './api'

const removeLoginToken = () => new Promise((resolve, reject) => {
	remove(`/auth-token/${getCookie('authToken')}`)
		.then(() => {
			delete api.defaults.headers.authorization
			resolve()
		})
		.catch((error) => {
			reject(error)
		})
})

const getLoginToken = (username, password) => new Promise((resolve, reject) => {
	post('/auth-token/', { username, password })
		.then((response) => {
			api.defaults.headers.authorization = `token ${response.data.token}`
			resolve(response)
		})
		.catch((error) => {
			reject(error)
		})
})

export {
	removeLoginToken,
	getLoginToken
}
