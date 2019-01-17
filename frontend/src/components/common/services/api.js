import axios from 'axios'
import tus from 'tus-js-client'

const logRequests = process.env.NODE_ENV === 'development'

// const BACKEND_HOST = 'localhost'
// const BACKEND_PORT = 8000
// let apiURL = `http://${BACKEND_HOST}:${BACKEND_PORT}/api/`;

let apiURL = `${window.location.origin}/api`
let apiBase = `${window.location.origin}`

const TUSD_HOST = 'localhost'
const TUSD_PORT = 1080
const _tusd_host = process.env.TUSD_HOST || TUSD_HOST
const _tusd_port = (process.env.TUSD_PORT && Number(process.env.TUSD_PORT)) || TUSD_PORT
const filesURL = `http://${_tusd_host}:${_tusd_port}/files/`

let isTestSession = false
if (process.env.NODE_ENV === 'development') {
	isTestSession = true
	apiURL = 'http://localhost:8000/api'
	apiBase = 'http://localhost:8000'
}

const api = axios.create({
	baseURL: apiURL,
	withCredentials: true
})

const apiPublicDirectory = axios.create()

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

const fetchFromPublicDirectory = (path) => {
	logRequests && console.log(`fetching ${path}...`)
	return apiPublicDirectory.get(path)
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

const getCurrentUser = () => fetch('current-user/')

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
	const params = {
		page_size: tableOptions.perPage,
		page: tableOptions.currentPage
	}
	if (tableOptions.filters) {
		params.current_state = tableOptions.filters.currentState
		params.search = tableOptions.filters.search
		params.party = tableOptions.filters.party
		params.obligation = tableOptions.filters.obligation
		params.from_period = tableOptions.filters.period_start
		params.to_period = tableOptions.filters.period_end
		if (tableOptions.filters.showAllVersions !== undefined) {
			params.is_current = tableOptions.filters.showAllVersions ? undefined : true
		}
	}
	if (tableOptions.sorting && tableOptions.sorting.sortBy) {
		params.ordering = (tableOptions.sorting.sortDesc ? '-' : '') + tableOptions.sorting.sortBy
	}

	return fetch('submissions/', { params })
}

const getPeriods = () => fetch('periods/')

const getObligations = () => fetch('obligations/')

const createSubmission = (submisson_data) => {
	console.log(api.defaults)
	return post('submissions/', submisson_data)
}

const createBlend = (blend) => post('blends/', blend)

const cloneSubmission = (url) => post(`${url}clone/`)

const getCustomBlends = (party) => fetch('blends/', { params: { party } })

const getSubmissionsVersions = () => fetch('submission-versions/')

const getInstructions = (formName, tabName) => {
	if (isTestSession) {
		return fetch(`${window.location.origin}/instructions/${formName}/${tabName}.html`)
	}
	return fetch(`${window.location.origin}/instructions/${tabName}.html`)
}

const deleteSubmission = (url) => remove(url)

const getSubmission = (url) => fetch(url)

const getSubmissionHistory = (url) => fetch(`${url}versions/`)

const callTransition = (url, transition) => post(`${url}call-transition/`, { transition })

const getNonParties = () => fetch('get-non-parties/')

const uploadAttachment = (attachment, submissionId, onProgressCallback) => new Promise(async (resolve, reject) => {
	const responseToken = await post(`submissions/${submissionId}/token/`)
	const upload = new tus.Upload(attachment,
		{
			endpoint: filesURL,
			metadata: {
				token: responseToken.data.token,
				filename: attachment.name
			},
			retryDelays: [0, 1000, 3000, 5000],
			onError: function onError(error) {
				console.log('File upload failed because: ', error)
				reject(error)
			},
			onProgress: function onProgress(bytesUploaded, bytesTotal) {
				if (onProgressCallback) {
					const percentage = parseInt(((bytesUploaded / bytesTotal) * 100).toFixed(2), 10)
					onProgressCallback(attachment, percentage)
				}
			},
			onSuccess: function onSuccess() {
				resolve(upload)
			}
		})
	upload.start()
})

export {
	apiURL,
	apiBase,
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
	getNonParties,
	getCurrentUser,
	uploadAttachment,
	fetchFromPublicDirectory
}
