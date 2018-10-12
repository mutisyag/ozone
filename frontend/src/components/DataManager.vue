<template>
  <div>
    <tabsmanager v-if="countryOptions && substances && blends" :data="{form: form, countryOptions: countryOptions, substances: substances, blends:blends}"></tabsmanager>
    <div v-else class="spinner">
      <div class="loader"></div>
    </div>
  </div>
</template>

<script>

import tabsManager from './TabsManager'
import form from '../assets/form.js'
import countryOptions from "@/assets/countryList.js"
import {getSubstances, getExportBlends, getParties} from '@/api/api.js'


export default {
  name: 'DataManager',
  components: {
    tabsmanager:tabsManager
  },


  data () {
    return {
      form: JSON.parse(JSON.stringify(form)),
      countryOptions: null,
      substances: null,
      blends: null,
    }
  },

  created() {
    this.getSubstances()
    this.importCountries()
  },

  methods: {

    // ASYNC IMPORT IS SO SLOW
    // importCountries(){
    //   import('@/assets/countryList.js').then( (response ) => {
    //     let module = response.default
    //     module().then( exported => {
    //       this.countryOptions = exported
    //     })
    //   });
    // },
    importCountries() {
      getParties().then(response => {
        let countryOptions = []
          for (let country of response.data) {
            countryOptions.push({ value: country.name, text: country.name})
          }
          this.countryOptions = countryOptions
      })
    },

    getSubstances(){
        getSubstances().then((response) => {
          this.substances = response.data 
          getExportBlends().then((response) => {
            this.blends = response.data
          })
        })
      }
  },
}
</script>

<style lang="css" scoped>

.spinner {
    z-index: 1;
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(0,0,0,0.2);
    display: flex;
    justify-content: center;
    align-items: center;
}

.loader {
  border: 16px solid #f3f3f3;
  border-radius: 50%;
   border-top: 16px solid blue;
   border-right: 16px solid green;
   border-bottom: 16px solid red;
   border-left: 16px solid pink;
  width: 120px;
  height: 120px;
  -webkit-animation: spin 2s linear infinite; /* Safari */
  animation: spin 2s linear infinite;
}

/* Safari */
@-webkit-keyframes spin {
  0% { -webkit-transform: rotate(0deg); }
  100% { -webkit-transform: rotate(360deg); }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>