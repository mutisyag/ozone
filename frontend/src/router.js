import Vue from 'vue'
import Router from 'vue-router'

// Containers
const DefaultContainer = () => import('@/containers/DefaultContainer')

// Views
const Dashboard = () => import('@/views/Dashboard')
const Form = () => import('@/views/Form')



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
      component: DefaultContainer,
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: Dashboard
        },
        {
          path: 'dashboard/form',
          name: 'Form',
          component: Form
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
          path: 'login',
          name: 'Login',
          component: Login
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
  base: '/',
}

const router = new Router(routerOptions);



router.beforeEach((to, from, next) => {
  console.log(to)
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