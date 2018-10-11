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
      url: '/form',
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
      url: '/form',
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
    {
      name: 'External link',
      url: 'http://ozone.unep.org',
      icon: 'icon-cloud-download',
      class: 'mt-auto',
      variant: 'success'
    },
  ]
}
