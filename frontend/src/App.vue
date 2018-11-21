<template>
  <div>
    
    <div class="api-action-display" v-if="isLoading">
      <div class="lds-ellipsis"><div></div><div></div><div></div><div></div></div>
    </div>  

    <router-view></router-view>
  
  </div>
</template>

<script>

import Router from './router'
import {api} from '@/api/api';
export default {
  name: 'app',
  components: {routerview: Router},
  data() {
    return {
      refCount: 0,
      isLoading: false
    }
  },
  methods: {
    setLoading(isLoading) {
      if (isLoading) {
        this.refCount++;
        this.isLoading = true;
      } else if (this.refCount > 0) {
        this.refCount--;
        this.isLoading = (this.refCount > 0);
      }
    }
  },
  created(){
    api.interceptors.request.use((config) => {
      this.setLoading(true);
      return config;
    }, (error) => {
      this.setLoading(false);
      return Promise.reject(error);
    });

    api.interceptors.response.use((response) => {
      this.setLoading(false);
      return response;
    }, (error) => {
      this.setLoading(false);
      return Promise.reject(error);
    });
  }

}
</script>

<style lang="scss">
  // CoreUI Icons Set
  @import '~@coreui/icons/css/coreui-icons.min.css';
  /* Import Font Awesome Icons Set */
  $fa-font-path: '~font-awesome/fonts/';
  @import '~font-awesome/scss/font-awesome.scss';
  /* Import Simple Line Icons Set */
  $simple-line-font-path: '~simple-line-icons/fonts/';
  @import '~simple-line-icons/scss/simple-line-icons.scss';
  /* Import Flag Icons Set */
  @import '~flag-icon-css/css/flag-icon.min.css';
  /* Import Bootstrap Vue Styles */
  @import '~bootstrap-vue/dist/bootstrap-vue.css';
  // Import Main styles for this application
  @import 'assets/scss/style';




  .lds-ellipsis {
  display: inline-block;
  position: relative;
  width: 64px;
  height: 64px;
}
.lds-ellipsis div {
  position: absolute;
  top: 27px;
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background: red;
  animation-timing-function: cubic-bezier(0, 1, 1, 0);
}
.lds-ellipsis div:nth-child(1) {
  left: 6px;
  background: yellow;
  animation: lds-ellipsis1 0.6s infinite;
}
.lds-ellipsis div:nth-child(2) {
  left: 6px;
  background: blue;
  animation: lds-ellipsis2 0.6s infinite;
}
.lds-ellipsis div:nth-child(3) {
  left: 26px;
  background: green;
  animation: lds-ellipsis2 0.6s infinite;
}
.lds-ellipsis div:nth-child(4) {
  left: 45px;
  animation: lds-ellipsis3 0.6s infinite;
}
@keyframes lds-ellipsis1 {
  0% {
    transform: scale(0);
  }
  100% {
    transform: scale(1);
  }
}
@keyframes lds-ellipsis3 {
  0% {
    transform: scale(1);
  }
  100% {
    transform: scale(0);
  }
}
@keyframes lds-ellipsis2 {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(19px, 0);
  }
}


.api-action-display {
  position: fixed;
  top:50%;
  left: 50%;
  transform: translate(-50%,-50%);
  z-index: 1000;
}
</style>
