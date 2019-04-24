const getNav = ($gettext) => [{
  name: $gettext('Dashboard'),
  url: '/dashboard',
  icon: 'icon-calculator'
},

{
  name: $gettext('Lookup tables'),
  icon: 'icon-list',
  children: [{
    name: $gettext('Substances'),
    url: '/lookup-tables/controlled-substances'
  }, {
    name: $gettext('Blends'),
    url: '/lookup-tables/blends'
  }, {
    name: $gettext('Parties'),
    url: '/lookup-tables/parties'
  }]
},

{
  name: $gettext('Production and consumption'),
  icon: 'icon-graph',
  url: '/reports/production-consumption'
}
]

export {
  getNav
}
