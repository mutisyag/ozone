import Vue from 'vue'
import Router from 'vue-router'
import Dashboard from '@/views/Dashboard'
import {
  apiBase
} from '@/components/common/services/api.js'

const Art7DataManager = () => import(/* webpackChunkName: "art7" */ '@/components/art7/DataManager')
const LetterDataManager = () => import(/* webpackChunkName: "letter" */ '@/components/letter/DataManager')
const HatDataManager = () => import(/* webpackChunkName: "hat" */ '@/components/hat/DataManager')
const RafDataManager = () => import(/* webpackChunkName: "hat" */ '@/components/raf/DataManager')

const ExemptionDataManager = () => import(/* webpackChunkName: "exemption" */ '@/components/exemption/DataManager')
// const FormNotFound = () => import(/* webpackChunkName: "notFound" */ '@/views/FormNotFound')
// Views - Pages
const Page404 = () => import(/* webpackChunkName: "404" */ '@/views/pages/Page404')
const UserProfile = () => import(/* webpackChunkName: "userProfile" */ '@/views/UserProfile')

const LookupTablesControlledSubstances = () => import(/* webpackChunkName: "lookup-tables" */ '@/views/lookupTables/ControlledSubstances')
const LookupTablesBlends = () => import(/* webpackChunkName: "lookup-tables" */ '@/views/lookupTables/Blends')
const LookupTablesParties = () => import(/* webpackChunkName: "lookup-tables" */ '@/views/lookupTables/Parties')
const ReportsProductionConsumption = () => import(/* webpackChunkName: "lookup-tables" */ '@/views/reports/Consumption')
const Reports = () => import(/* webpackChunkName: "reports" */ '@/views/Reports')

Vue.use(Router)

const routes = [{
  path: '/',
  name: 'Home',
  redirect: '/dashboard'
},
{
  path: '/dashboard',
  name: 'Dashboard',
  meta: {
    requiresAuth: true
  },
  component: Dashboard
},
{
  path: '/user-profile',
  name: 'UserProfile',
  meta: {
    requiresAuth: true
  },
  component: UserProfile
},
{
  path: '/login',
  beforeEnter() {
    window.location = `${apiBase}/admin/login/?next=${encodeURIComponent(window.location.href)}`
  },
  name: 'Login'
},
{
  path: '/submission',
  name: 'Submission',
  component: {
    render(c) {
      return c('router-view')
    }
  },
  children: [{
    path: 'art7',
    name: 'art7',
    meta: {
      requiresAuth: true,
      title: 'Article 7'
    },
    component: Art7DataManager
  },
  {
    path: 'essencrit',
    name: 'essencrit',
    meta: {
      requiresAuth: true
    },
    component: RafDataManager
  },
  {
    path: 'hat',
    name: 'hat',
    meta: {
      requiresAuth: true
    },
    component: HatDataManager
  },
  {
    path: 'other',
    name: 'other',
    meta: {
      requiresAuth: true
    },
    component: LetterDataManager
  },
  {
    path: 'exemption',
    name: 'exemption',
    meta: {
      requiresAuth: true
    },
    component: ExemptionDataManager
  }
  ]
},
{
  path: '/pages',
  redirect: '/pages/404',
  name: 'Pages',
  component: {
    render(c) {
      return c('router-view')
    }
  },
  children: [{
    path: '404',
    name: 'Page404',
    component: Page404
  }]
},
{
  path: '/lookup-tables',
  redirect: '/pages/404',
  name: 'Lookup tables',
  component: {
    render(c) {
      return c('router-view')
    }
  },
  children: [{
    path: 'controlled-substances',
    name: 'Controlled Substances',
    component: LookupTablesControlledSubstances
  },
  {
    path: 'blends',
    name: 'Blends',
    component: LookupTablesBlends
  },
  {
    path: 'parties',
    name: 'Parties',
    component: LookupTablesParties
  }
  ]
},
{
  path: '/reports',
  name: 'Reports',
  component: Reports,
  children: [{
    path: 'production-consumption',
    name: 'Production and consumption',
    component: ReportsProductionConsumption
  }
  ]
}
]

const routerOptions = {
  routes,
  linkActiveClass: 'open active',
  mode: 'history',
  scrollBehavior: () => ({
    y: 0
  }),
  base: '/reporting'
}

const router = new Router(routerOptions)

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const authToken = window.$cookies.get('authToken')

    if (!authToken) {
      next({
        name: 'Login'
      })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
