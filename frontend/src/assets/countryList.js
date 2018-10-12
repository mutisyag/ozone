// var countryOptions = []
import {getParties} from '@/api/api'
let countryOptions = []

async function load() {
  await getParties().then( (response) => {
    for (let country of response.data) {
      countryOptions.push({ value: country.name, text: country.name})
    }
  });
}

export default async () => {
  await load();
  return countryOptions;
}