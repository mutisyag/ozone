const getNav = ($gettext) => [
	{
		name: $gettext('Dashboard'),
		url: '/dashboard',
		icon: 'icon-calculator'
	},

	{
		name: $gettext('Lookup tables'),
		icon: 'icon-list',
		children: [{
			name: $gettext('Controlled substances'),
			url: '/lookup-tables/controlled-substances'
		}, {
			name: $gettext('Blends'),
			url: '/lookup-tables/blends'
		}, {
			name: $gettext('Parties'),
			url: '/lookup-tables/parties'
		}]
	}
	// {
	//   title: true,
	//   name: 'Art. 7'
	// },
	// {
	//   name: 'New submission',
	//   icon: 'icon-docs',
	//   url: '/dashboard/form',
	// },
	// {
	//   title: true,
	//   name: 'Non-art 7',
	//   class: '',
	//   wrapper: {
	//     element: '',
	//     attributes: {}
	//   }
	// },
	// {
	//   name: 'Letter',
	//   icon: 'icon-docs',
	//   url: '/dashboard/form',
	//   badge: {
	//     variant: 'primary',
	//     text: 'demo'
	//   },
	// },
	// {
	//   title: true,
	//   name: 'Lookup tables',
	//   class: '',
	//   wrapper: {
	//     element: '',
	//     attributes: {}
	//   }
	// },
	// {
	//   name: 'Report Centre',
	//   url: '/base',
	//   icon: 'icon-puzzle',
	//   children: [
	//     {
	//       name: 'Menu sub item',
	//       url: '/base/forms',
	//       icon: 'icon-puzzle'
	//     }
	//   ]
	// },

	// {
	//   name: 'User',
	//   url: '/pages',
	//   icon: 'icon-star',
	//   children: [
	//     {
	//       name: 'Login',
	//       url: '/login',
	//       icon: 'icon-star'
	//     },
	//     {
	//       name: 'Register',
	//       url: '/register',
	//       icon: 'icon-star'
	//     },
	//     {
	//       name: 'Logout',
	//       url: '/logout',
	//       icon: 'icon-star'
	//     },
	//     {
	//       name: 'Profile',
	//       url: '/profile',
	//       icon: 'icon-star'
	//     }
	//   ]
	// },

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

export {
	getNav
}
