import Vue from 'vue'
import Router from 'vue-router'

// Containers
const Base = () => import('@/views/Base')

// Views
const Dashboard = () => import('@/views/Dashboard')
const Form = () => import('@/views/Form')

const FormNotFound = () => import('@/views/FormNotFound')

// Views - Components
const Forms = () => import('@/views/base/Forms')

// Views - Pages
const Page404 = () => import('@/views/pages/Page404')
const Page500 = () => import('@/views/pages/Page500')
const Login = () => import('@/views/pages/Login')
const Register = () => import('@/views/pages/Register')

// Users
const Users = () => import('@/views/users/Users')
const User = () => import('@/views/users/User')

Vue.use(Router)

const  routes = [
    {
      path: '/',
      redirect: '/dashboard',
      name: 'Home',
      component: Base,
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          meta:{requiresAuth : true},
          component: Dashboard
        },
        {
          path: 'login',
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
          path: 'users',
          meta: { label: 'Users'},
          component: {
            render (c) { return c('router-view') }
          },
          children: [
            {
              path: '',
              component: Users,
            },
            {
              path: ':id',
              meta: { label: 'User Details'},
              name: 'User',
              component: User,
            },
          ]
        },
        {
          path: 'base',
          redirect: '/base/forms',
          name: 'Base',
          component: {
            render (c) { return c('router-view') }
          },
          children: [
            {
              path: 'forms',
              name: 'Forms',
              component: Forms
            },
          ]
        },
      ]
    },
    {
      path: '/pages',
      redirect: '/pages/404',
      name: 'Pages',
      component: {
        render (c) { return c('router-view') }
      },
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
  console.log('to',to)
  if (to.meta.requiresAuth) {
    console.log(window)
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