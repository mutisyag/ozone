const state = {
  currentUser: null,
  actionToDispatch: null,
  submissionDefaultValues: null,
  dataForAction: null,
  dashboard: {
    mySubmissions: null,
    submissions: null,
    periods: null,
    obligations: null,
    parties: null,
    table: {
      currentPage: 1,
      perPage: 10,
      totalRows: 0,
      sorting: {
        sortBy: 'updated_at',
        sortDesc: true,
        sortDirection: 'asc'
      },
      filters: {
        search: null,
        period_start: null,
        is_superseded: null,
        period_end: null,
        obligation: null,
        party: null,
        isCurrent: null
      }
    }
  },
  currentAlert: {
    message: null,
    show: false,
    variant: null
  },
  confirmModal: {
    isVisible: false,
    title: null,
    description: null,
    okCallback: () => {},
    cancelCallback: () => {}
  },
  current_submission: null,
  route: '',
  currentSubmissionHistory: null,
  permissions: {
    dashboard: null,
    form: null,
    actions: null
  },
  tableRowConstructor: null,
  newTabs: [],
  form: null,
  initialData: {
    countryOptions: null,
    countryOptionsSubInfo: null,
    groupSubstances: null,
    substances: null,
    partyRatifications: null,
    essenCritTypes: null,
    submissionFormats: null,
    blends: null,
    nonParties: null,
    display: {
      substances: null,
      blends: null,
      countries: null
    }
  },
  alertData: []
}

export default state
