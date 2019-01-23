<template>
  <div class="app">
    <div class="api-action-display" v-if="isLoading">
      <div class="lds-ellipsis"><div></div><div></div><div></div><div></div></div>
    </div>
    <AppHeader fixed>
      <SidebarToggler class="d-lg-none" display="md" mobile />
      <!-- <b-link class="navbar-brand" to="#"> -->
        <!-- <img class="navbar-brand-full" width="89" height="25" alt="Logo"> -->
        <!-- <img class="navbar-brand-minimized" width="30" height="30" alt="MobileLogo"> -->
      <!-- </b-link> -->
      <SidebarToggler class="d-md-down-none" display="lg" />
      <h3><span v-translate>ORS (Ozone online reporting system)</span></h3>

      <b-navbar-nav class="ml-auto">
		<Header/>
      </b-navbar-nav>
      <!--<AsideToggler class="d-lg-none" mobile />-->
    </AppHeader>
    <div class="app-body">
      <AppSidebar fixed>
        <SidebarHeader/>
        <SidebarForm/>
        <SidebarNav :navItems="nav"></SidebarNav>
        <SidebarFooter/>
        <SidebarMinimizer/>
      </AppSidebar>

      <main class="main">
		<div class="breadcrumb">
			{{list}}
		</div>
        <div class="container-fluid">
          <router-view></router-view>
        </div>
      </main>
    </div>
  </div>
</template>

<script>

import { getNav } from '@/_nav'
import {
	Header as AppHeader, SidebarToggler, Sidebar as AppSidebar, SidebarFooter, SidebarForm, SidebarHeader, SidebarMinimizer, SidebarNav
} from '@coreui/vue'
import Header from '@/components/common/Header'
import { api } from '@/components/common/services/api'
import auth from '@/components/common/mixins/auth'

export default {
	name: 'app',
	components: {
		AppHeader,
		AppSidebar,
		Header,
		SidebarForm,
		SidebarFooter,
		SidebarToggler,
		SidebarHeader,
		SidebarNav,
		SidebarMinimizer
	},

	mixins: [auth],

	data() {
		return {
			refCount: 0,
			isLoading: false,
			nav: getNav(this.$gettext)

		}
	},

	computed: {
		name() {
			return this.$route.name
		},
		list() {
			console.log('list.......', this.$store.state.route)
			return this.$store.state.route
		}
	},
	methods: {
		setLoading(isLoading) {
			if (isLoading) {
				this.refCount += 1
				this.isLoading = true
			} else if (this.refCount > 0) {
				this.refCount -= 1
				this.isLoading = (this.refCount > 0)
			}
		}
	},
	watch: {
		'$language.current': {
			handler() {
				this.nav = getNav(this.$gettext)
			}
		}
	},
	created() {
		api.interceptors.request.use((config) => {
			if (!config.hideLoader) {
				this.setLoading(true)
			}
			return config
		}, (error) => {
			this.setLoading(false)
			this.$store.dispatch('setAlert', {
				$gettext: this.$gettext,
				message: { ...error.response.data },
				variant: 'danger'
			})
			return Promise.reject(error)
		})

		api.interceptors.response.use((response) => {
			this.setLoading(false)
			return response
		}, (error) => {
			this.setLoading(false)
			this.$store.dispatch('setAlert', {
				$gettext: this.$gettext,
				message: { ...error.response.data },
				variant: 'danger'
			})
			if (error.response.status === 401) {
				this.logout('cookie')
			}

			return Promise.reject(error)
		})
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
