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

const fetch = (path, config = null) => {
	logRequests && console.log(`fetching ${path}...`)
	checkAuth()
	return api.get(path, config)
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

const getPartyRatifications = () => fetch('get-party-ratifications/')

const getExportBlends = () => {
	if (isTestSession) {
		console.log('getting blends')
		return axios.get(`${window.location.origin}/blends.json`)
	}
	return null
}

const getSubmissions = (tableOptions) => {
	return fetch('submissions/', {
		"params": {
			page_size: tableOptions.perPage,
			page: tableOptions.currentPage,
			search: tableOptions.filters.search,
			party: tableOptions.filters.party,
			obligation: tableOptions.filters.obligation,
			from_period: tableOptions.filters.period_start,
			to_period: tableOptions.filters.period_end,
			ordering: (tableOptions.sorting.sortDesc ? "-" : "") + tableOptions.sorting.sortBy
		}
	})
}

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

const getInstructions = (tabName) => {
	if (isTestSession) {
		return fetch(`http://localhost:8080/instructions/${tabName}.html/`)
	}
	return fetch(`${window.location.origin}/instructions/${tabName}.html`)
}

const deleteSubmission = (url) => remove(url)

const getSubmission = (url) => fetch(url)

const getSubmissionHistory = (url) => fetch(`${url}history/`)

const callTransition = (url, transition) => post(`${url}call-transition/`, { transition })

const getNonParties = () => fetch('get-non-parties/')

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
	getPartyRatifications,
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
	getSubmissionHistory,
	getNonParties
}
