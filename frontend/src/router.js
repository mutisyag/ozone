import Vue from 'vue'
import Router from 'vue-router'

import App from './App'
import Dashboard from '@/views/Dashboard'


const Form = () => import(/* webpackChunkName: "art7" */ '@/views/Form')
const FormNotFound = () => import(/* webpackChunkName: "notFound" */ '@/views/FormNotFound')
// Views - Pages
const Page404 = () => import(/* webpackChunkName: "404" */ '@/views/pages/Page404')
const Page500 = () => import(/* webpackChunkName: "500" */ '@/views/pages/Page500')
const Login = () => import(/* webpackChunkName: "login" */ '@/views/pages/Login')
const Register = () => import(/* webpackChunkName: "register" */ '@/views/pages/Register')


Vue.use(Router)

const  routes = [
    {
      path: '/',
      name: 'Home',
      component: Dashboard,
      redirect: '/dashboard'
      // component: {
      //   render (c) { return c('router-view') }
      // },
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      meta:{requiresAuth : true},
      component: Dashboard
    },
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/submission/art7',
      name: 'art7',
      meta:{requiresAuth : true},
      component: Form
    },
    {
      path: '/submission/essencrit',
      name: 'essencrit',
      meta:{requiresAuth : true},
      component: FormNotFound
    },
    {
      path: '/submission/hatimp',
      name: 'hatimp',
      meta:{requiresAuth : true},
      component: FormNotFound
    },
    {
      path: '/submission/hatprod',
      name: 'hatprod',
      meta:{requiresAuth : true},
      component: FormNotFound
    },
    {
      path: '/submission/letter',
      name: 'letter',
      meta:{requiresAuth : true},
      component: FormNotFound
    },
    {
      path: '/pages',
      redirect: '/pages/404',
      name: 'Pages',
 
      children: [
        {
          path: '404',
          name: 'Page404',
          component: Page404
        },
        {
          path: '500',
          name: 'Page500',
          component: Page500
        },
        {
          path: 'register',
          name: 'Register',
          component: Register
        }
      ]
    }
  ]


const routerOptions = {
  routes,
  linkActiveClass: 'open active',
  mode:'history',
  scrollBehavior: (to, from, savedPosition) => ({ y: 0 }),
  base: '/reporting',
}

const router = new Router(routerOptions);



router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const authToken = window.$cookies.get('authToken');
    
    if (!authToken) {
      next({ name:'Login' });
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router