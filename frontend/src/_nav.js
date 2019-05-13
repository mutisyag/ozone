const getNav = ($gettext) => [{
  name: $gettext('Dashboard'),
  url: '/dashboard',
  icon: 'icon-screen-desktop'
},
{
  name: $gettext('Substances'),
  url: '/lookup-tables/controlled-substances',
  icon: 'icon-chemistry'
}, {
  name: $gettext('Blends'),
  url: '/lookup-tables/blends',
  icon: 'icon-layers'
}, {
  name: $gettext('Parties'),
  url: '/lookup-tables/parties',
  icon: 'icon-people'
},
{
  name: $gettext('Production'),
  icon: 'icon-graph',
  url: '/reports/production-consumption'
}
]

export {
  getNav
}
