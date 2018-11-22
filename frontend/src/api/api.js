/* eslint-disable */
import axios from 'axios';

const logRequests = process.env.NODE_ENV === 'development';

const BACKEND_HOST = 'localhost';
const BACKEND_PORT = 8000;

let apiURL = `http://${BACKEND_HOST}:${BACKEND_PORT}/api/`;

const api = axios.create({
  baseURL: apiURL,
  withCredentials: true,
});

let isTestSession = true
if(isTestSession) {
 apiURL = `http://localhost:8080`;
}

api.defaults.xsrfHeaderName = "X-CSRFTOKEN";
api.defaults.xsrfCookieName = "csrftoken";

function checkAuth() {
  if (!api.defaults.headers['authorization'] && getCookie('authToken')) {
    api.defaults.headers.authorization = 'token ' + getCookie('authToken');
  }
}

function fetch(path) {
  logRequests && console.log(`fetching ${path}...`);
  checkAuth();
  return api.get(path);
}

function post(path, data) {
  logRequests && console.log(`posting ${path} with data ${data}...`);
  checkAuth();
  return api.post(path, data);
}

function update(path, data) {
  logRequests && console.log(`patching ${path} with data ${data}...`);
  checkAuth();
  return api.put(path, data);
}

function remove(path) {
  logRequests && console.log(`removig ${path} ...`);
  checkAuth();
  return api.delete(path);
}

function getCookie(name) {
  let cookie = {};
  document.cookie.split(';').forEach(function (el) {
    let [k, v] = el.split('=');
    cookie[k.trim()] = v;
  })
  return cookie[name];
}


 function getSubstances() {
    return fetch('group-substances/')
}

 function getUsers() {
    return fetch('users/')
}


function getParties() {
    return fetch('parties/')
}

 function getExportBlends() {
  if(isTestSession) {
    console.log('getting blends')
    return axios.get(window.location.origin + '/blends.json')
  }
}

function getSubmissions(){
  return fetch('submissions/')
}

function getPeriods(){
  return fetch('periods/')
}

function getObligations(){
  return fetch('obligations/')
}


function createSubmission(submisson_data){
  console.log(api.defaults)
  return post('submissions/', submisson_data)
}


function createBlend(blend){
  return post('blends/', blend)
}

function getCustomBlends(){
  return fetch('blends/')
}

function getSubmissionsVersions(){
  return fetch('submission-versions/')
}

 function getInstructions() {
  if(isTestSession) {
    return fetch(window.location.origin + '/test.html')
  }
}


function deleteSubmission(url) {
  return remove(url)
}

function getSubmission(url) {
  return api.get(url)
}


function callTransition(url, transition) {
  return post(`${url}call-transition/`, {transition: transition})
}


export { 
 apiURL,
 filesURL,
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
 deleteSubmission
};
