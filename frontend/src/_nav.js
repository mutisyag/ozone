export default {
  items: [
    {
      name: 'Dashboard',
      url: '/dashboard'
    },
    {
      title: true,
      name: 'Art. 7'
    },
    {
      name: 'New submission',
      icon: 'icon-docs',
      url: '/dashboard/form',
    },
    {
      title: true,
      name: 'Non-art 7',
      class: '',
      wrapper: {
        element: '',
        attributes: {}
      }
    },
    {
      name: 'Letter',
      icon: 'icon-docs',
      url: '/dashboard/form',
      badge: {
        variant: 'primary',
        text: 'demo'
      },
    },
    {
      divider: true
    },
    {
      title: true,
      name: 'Lookup tables',
      class: '',
      wrapper: {
        element: '',
        attributes: {}
      }
    },
    {
      name: 'Report Centre',
      url: '/base',
      icon: 'icon-puzzle',
      children: [
        {
          name: 'Menu sub item',
          url: '/base/forms',
          icon: 'icon-puzzle'
        }
      ]
    },
    {
      divider: true
    },
    {
      title: true,
      name: 'Extras'
    },
    {
      name: 'Pages',
      url: '/pages',
      icon: 'icon-star',
      children: [
        {
          name: 'Login',
          url: '/pages/login',
          icon: 'icon-star'
        },
        {
          name: 'Register',
          url: '/pages/register',
          icon: 'icon-star'
        },
        {
          name: 'Error 404',
          url: '/pages/404',
          icon: 'icon-star'
        },
        {
          name: 'Error 500',
          url: '/pages/500',
          icon: 'icon-star'
        }
      ]
    },

   
   // {
   //    name: 'Form status legend',
   //    // url: '/pages',
   //    // icon: 'icon-star',
   //    children: [
   //      {
   //        name: 'Edited',
   //        icon: 'fa fa-edit fa-lg',
   //      },
   //      {
   //        name: 'Invalid',
   //        icon: 'fa fa-times-circle fa-lg',
   //        variant: 'danger'
   //      },      
   //      {
   //        name: 'Edited',
   //        icon: 'fa fa-check-circle fa-lg',
   //        variant: 'success',
   //      },      
   //      {
   //        name: 'Edited',
   //        icon: 'fa fa-edit fa-lg'
   //      },
   //    ]
   //  },


   
  ]
}
