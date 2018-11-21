<template>
  <div class="app">
    <Alerts></Alerts>  
    <AppHeader fixed>
      <SidebarToggler class="d-lg-none" display="md" mobile />
      <!-- <b-link class="navbar-brand" to="#"> -->
        <!-- <img class="navbar-brand-full" width="89" height="25" alt="Logo"> -->
        <!-- <img class="navbar-brand-minimized" width="30" height="30" alt="MobileLogo"> -->
      <!-- </b-link> -->
      <SidebarToggler class="d-md-down-none" display="lg" />
      <b-navbar-nav class="ml-auto">
        <b-nav-item class="d-md-down-none">
          <i class="icon-bell"></i>
          <b-badge pill variant="danger">5</b-badge>
        </b-nav-item>
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
        <Breadcrumb :list="list"/>
        <div class="container-fluid">
          <router-view></router-view>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import nav from '@/_nav'
import Alerts from './Alerts'
import { Header as AppHeader, SidebarToggler, Sidebar as AppSidebar, SidebarFooter, SidebarForm, SidebarHeader, SidebarMinimizer, SidebarNav, Aside as AppAside, Footer as TheFooter, Breadcrumb } from '@coreui/vue'
import Header from './Header'

export default {
  name: 'full',
  components: {
    AppHeader,
    AppSidebar,
    AppAside,
    TheFooter,
    Breadcrumb,
    Header,
    SidebarForm,
    SidebarFooter,
    SidebarToggler,
    SidebarHeader,
    SidebarNav,
    SidebarMinimizer,
    Alerts
  },
  data () {
    return {
      nav: nav.items
    }
  },
  computed: {
    name () {
      return this.$route.name
    },
    list () {
      return this.$route.matched.filter((route) => route.name || route.meta.label )
    }
  }
}
</script>
