// needed for axios to run in IE11
// import 'promise-polyfill/src/polyfill';

// used for http requests
import axios from 'axios';



// api instance
const api = axios.create({
  withCredentials: true
})

function fetch(path) {
  return api.get(path);
}

function post(path, data) {
  return api.post(path, data);
}



// environment variable
let isTestSession = true;

console.log(process.env.NODE_ENV)
if (process.env.NODE_ENV === 'production') {
  isTestSession = false;
}



export function getImportSubstances() {
  if(isTestSession) {
    return fetch(window.location.origin + '/substances.json')
  }
}


export function getExportBlends() {
  if(isTestSession) {
    return fetch(window.location.origin + '/blends.json')
  }
}




export function getInstructions() {
  if(isTestSession) {
    return fetch(window.location.origin + '/test.html')
  }
}


// used for uploading file from within the webform
export function uploadFile(file) {
  var uploadUri;
  var domain = getDomain(window.location.href);
  var webqUri = getWebQUrl('/restProxyFileUpload');
  uploadUri = domain + webqUri + "&uri=" + envelope + "/manage_addDocument";

  return axios({
    method: 'post',
    withCredentials: true,
    async: false,
    cache: false,
    contentType: false,
    processData: false,
    url: uploadUri,
    data: file
  })

}
