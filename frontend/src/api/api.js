import axios from 'axios'

const logRequests = process.env.NODE_ENV === 'development'

// const BACKEND_HOST = 'localhost'
// const BACKEND_PORT = 8000
// let apiURL = `http://${BACKEND_HOST}:${BACKEND_PORT}/api/`;

let apiURL = `${window.location.origin}/api`

let isTestSession = false
if (process.env.NODE_ENV === 'development') {
	isTestSession = true
	apiURL = 'http://localhost:8000/api'
}

const api = axios.create({
	baseURL: apiURL,
	withCredentials: true
})

api.defaults.xsrfHeaderName = 'X-CSRFTOKEN'
api.defaults.xsrfCookieName = 'csrftoken'

const getCookie = (name) => {
	const cookie = {}
	document.cookie.split(';').forEach((el) => {
		const [k, v] = el.split('=')
		cookie[k.trim()] = v
	})
	return cookie[name]
}

const checkAuth = () => {
	if (!api.defaults.headers.authorization && getCookie('authToken')) {
		api.defaults.headers.authorization = `token ${getCookie('authToken')}`
	}
}

const fetch = (path) => {
	logRequests && console.log(`fetching ${path}...`)
	checkAuth()
	return api.get(path)
}

const post = (path, data) => {
	logRequests && console.log(`posting ${path} with data ${data}...`)
	checkAuth()
	return api.post(path, data)
}

const update = (path, data) => {
	logRequests && console.log(`patching ${path} with data ${data}...`)
	checkAuth()
	return api.put(path, data)
}

const remove = (path) => {
	logRequests && console.log(`removig ${path} ...`)
	checkAuth()
	return api.delete(path)
}

const getSubstances = () => fetch('group-substances/')

const getUsers = () => fetch('users/')

const getParties = () => fetch('parties/')

const getExportBlends = () => {
	if (isTestSession) {
		console.log('getting blends')
		return axios.get(`${window.location.origin}/blends.json`)
	}
	return null
}

const getSubmissions = () => fetch('submissions/')

const getPeriods = () => fetch('periods/')

const getObligations = () => fetch('obligations/')

const createSubmission = (submisson_data) => {
	console.log(api.defaults)
	return post('submissions/', submisson_data)
}

const createBlend = (blend) => post('blends/', blend)

const cloneSubmission = (url) => post(`${url}clone/`)

const getCustomBlends = () => fetch('blends/')

const getSubmissionsVersions = () => fetch('submission-versions/')

const getInstructions = () => {
	if (isTestSession) {
		return fetch(`${window.location.origin}/test.html`)
	}
	return null
}

const deleteSubmission = (url) => remove(url)

const getSubmission = (url) => api.get(url)

const getSubmissionHistory = (url) => api.get(`${url}history/`)

const callTransition = (url, transition) => post(`${url}call-transition/`, { transition })

export {
	apiURL,
	api,
	fetch,
	post,
	update,
	remove,
	getCookie,
	getSubstances,
	getExportBlends,
	getInstructions,
	getUsers,
	getParties,
	getSubmissions,
	getPeriods,
	getObligations,
	createSubmission,
	getSubmission,
	createBlend,
	getCustomBlends,
	getSubmissionsVersions,
	callTransition,
	deleteSubmission,
	cloneSubmission,
	getSubmissionHistory
}
