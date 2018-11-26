import Vue from 'vue'
import Vuex from 'vuex'
import form from '@/assets/form.js'
import tableRowConstructor from '@/mixins/tableRowConstructor'
import { fetch, callTransition, getSubstances, getExportBlends, getSubmission, getCustomBlends, deleteSubmission, getSubmissions, getPeriods, getObligations, createSubmission, getParties } from '@/api/api.js'

import dummyTransition from '@/assets/dummyTransition.js'

Vue.use(Vuex)

function intersect(a, b) {
    var setA = new Set(a);
    var setB = new Set(b);
    var intersection = new Set([...setA].filter(x => setB.has(x)));
    return Array.from(intersection);
}

const store = new Vuex.Store({
    // strict: true,
    state: {
        dashboard: {
            submissions: null,
            periods: null,
            obligations: null,
            parties: null,
        },
        currentAlert: {
            message: null,
            show: false,
            variant: null,
        },
        baseForm: form,
        current_submission: null,
        available_transitions: null,
        permissions: {
            dashboard: null,
            form: null,
            actions: null,
        },
        newTabs: [],
        form: null,
        initialData: {
            countryOptions: null,
            substances: null,
            blends: null,
            display: {
                substances: null,
                blends: null,
                countries: null,
            }
        },
    },


    getters: {
        // ...
        getValidationForCurrentTab: (state) => (tab) => {
            if(['edited',false].includes(state.form.tabs[tab].status)){
                return state.form.tabs[tab].form_fields.map(field => field.validation.selected ?
                    { validation: field.validation.selected, substance: field.substance.selected, blend: field.blend ? field.blend.selected : null } :
                    null)
            }
        },


        getDuplicateSubmission: (state) => (data) => {
            return state.dashboard.submissions.filter(
                (sub) => {
                    return sub.obligation === data.obligation &&
                        sub.party === data.party &&
                        sub.reporting_period === data.reporting_period
                })
        },

        getPeriodYear: (state) => (periodId) => {
            return state.dashboard.periods.find( (period) => { return period.value === periodId}).end_date
        },

        checkIfBlendAlreadyEists: (state) => (blendName) => {
            return state.initialData.blends.find( (blend) => { return blend.blend_id === blendName})
        },

        transitionState: (state) => {
            const currentState = state.permissions.form
            const availableTransitions = state.available_transitions || []

            let tstate = null
            if (intersect(currentState, ['edit', 'save']).length)
                tstate = false
            else
                tstate = true

            if (!availableTransitions.includes('submit')) {
                tstate = true
            }

            return tstate
        },
    },

    actions: {

        addSubmission(context, data) {

            return new Promise((resolve, reject) => {
                const duplicate = context.getters.getDuplicateSubmission(data)
                const submissionYear = new Date(context.getters.getPeriodYear(data.reporting_period))
                if (duplicate.length) {
                    context.dispatch('setAlert', { message: 'Another submission already exists in Data Entry stage.', variant: 'danger' })
                } else if(submissionYear > new Date()) {
                    context.dispatch('setAlert', { message: 'You can\'t report for this period yet', variant: 'danger' })
                } else {
                    createSubmission(data).then((response) => {
                        context.dispatch('getCurrentSubmissions')
                        context.dispatch('setAlert', { message: 'Submission Created', variant: 'success' })
                        resolve(response.data)
                    }).catch((error) => {
                        context.dispatch('setAlert', { message: 'Failed to create submission', variant: 'danger' })
                        reject(error.response)
                    })
                }
            });

        },

        getCurrentSubmissions(context) {
            getSubmissions().then(response => {
                context.commit('setDashboardSubmissions', response.data)
            })
        },

        getDashboardParties(context) {
            getParties().then(response => {
                const parties_temp = response.data
                                        .filter( country => country.id === country.parent_party )
                                        .map( country => {
                                            return { value: country.id, text: country.name}                 
                                        })
                context.commit('setDashboardParties', parties_temp)
            })
        },
        getDashboardPeriods(context) {
            getPeriods().then(response => {
                let current_date = new Date();
                let sortedPeriods = response.data
                                    .filter( a => new Date(a.end_date) < current_date)
                                    .sort((a, b) => { 
                                        return (parseInt(b.end_date.split('-')[0]) - parseInt(a.end_date.split('-')[0])) === 0
                                        ?
                                        (parseInt(b.start_date.split('-')[0]) - parseInt(a.start_date.split('-')[0]))
                                        :
                                        (parseInt(b.end_date.split('-')[0]) - parseInt(a.end_date.split('-')[0]))
                                    })
                                    .sort((a, b) => { return  b.is_year - a.is_year })
               sortedPeriods = sortedPeriods.map( (period) => {
                    let start = period.start_date.split('-')[0]
                    let end = period.end_date.split('-')[0]
                    let periodDisplay = ''
                    start === end ? periodDisplay += start : periodDisplay += start + '-' + end
                    return { value: period.id, text: `${period.name} (${periodDisplay})`, end_date: period.end_date, start_date: period.start_date}
               })
                
                context.commit('setDashboardPeriods', sortedPeriods)
            })
        },

        getDashboardObligations(context) {
            getObligations().then(response => {
                let obligations_temp = [];
                for (let obligation of response.data) {
                    obligations_temp.push({ value: obligation.id, text: obligation.name, form_type: obligation.form_type})
                }
                context.commit('setDashboardObligations', obligations_temp)
            })
        },


        resetAlert(context) {
            return new Promise((resolve, reject) => {
                context.commit('setCurrentAlertMessage', null)
                context.commit('setCurrentAlertVisibility', false)
                context.commit('setCurrentAlertVariant', null)
                resolve()
            });
        },

        setAlert(context, data) {
            context.dispatch('resetAlert').then(r => {
                context.commit('setCurrentAlertMessage', data.message)
                context.commit('setCurrentAlertVisibility', true)
                context.commit('setCurrentAlertVariant', data.variant)
            })
        },

        prefillQuestionaire(context, data) {
            Object.keys(context.state.current_submission.article7questionnaire).forEach((element, index) => {
                context.commit('updateQuestionaireField', { value: context.state.current_submission.article7questionnaire[element], field: element })
            });
        },


        doSubmissionTransition(context, data) {
            callTransition(data.submission, data.transition).then((response) => {
                context.dispatch('getSubmissionData', data.submission)
                context.dispatch('setAlert', { message: 'Submission state updated', variant: 'success' })
            }).catch( error => {
                context.dispatch('setAlert', { message: 'Unable to change the state of this submission', variant: 'danger' })
                console.log(error)
            })
        },

        removeSubmission(context, submissionUrl) {
            deleteSubmission(submissionUrl).then((response) => {
                context.dispatch('getCurrentSubmissions')
                context.dispatch('setAlert', { message: 'Submission deleted', variant: 'success' })
            }).catch(error => {
                context.dispatch('getCurrentSubmissions')
                context.dispatch('setAlert', { message: 'Failed to delete submission', variant: 'danger' })
            })
        },


        getInitialData(context, data) {
            context.commit('getEmptyForm')
            return new Promise((resolve, reject) => {
                context.dispatch('getSubmissionData',data).then(r => {
                    context.dispatch('getCountries')
                    context.dispatch('getSubstances')
                    context.dispatch('getCustomBlends')
                    resolve()
                })
            });
        },



        getSubmissionData(context, data) {
            return new Promise((resolve, reject) => {
                getSubmission(data).then((response) => {
                    context.commit('updateSubmissionData', response.data)
                    context.commit('updateAvailableTransitions', response.data.available_transitions)
                    if (context.state.current_submission.article7questionnaire) {
                        context.dispatch('prefillQuestionaire')
                    }
                    context.commit('updateFormPermissions', dummyTransition)
                    resolve()
                })

            });

        },



        getCountries(context) {
            let countryDisplay = {}
            getParties().then(response => {
                let countryOptions  = response.data.filter((p)=>{
                    countryDisplay[p.id] = p.name
                    return p.id != context.state.current_submission.party
                }).map((country) => {
                    return { value: country.id, text: country.name }
                })
                context.commit('updateCountries', countryOptions)
                context.commit('updateCountriesDisplay', countryDisplay)
            })
        },

        getSubstances(context) {
            let tempSubstances = []
            let substancesDisplay = {}
            getSubstances().then((response) => {
                for (let group of response.data) {
                    group.substances.sort( (a,b) => {return a.sort_order - b.sort_order})
                    for (let substance of group.substances) {
                        tempSubstances.push({ value: substance.id, text: substance.name, group: group })
                        substancesDisplay[substance.id] = substance.name
                    }
                }
                context.commit('updateSubstances', tempSubstances)
                context.commit('updateSubstancesDisplay', substancesDisplay)
            })
        },

        getCustomBlends(context) {
            let blendsDisplay = {}
            getCustomBlends().then((response) => {
                for (let blend of response.data) {
                    blendsDisplay[blend.id] = { name: blend.blend_id, components: blend.components }
                }
                context.commit('updateBlends', response.data)
                context.commit('updateBlendsDisplay', blendsDisplay)
            })
        },


        createSubstance(context, data) {
            let iterator = data.substanceList
            let substancesHere = (data.substanceList && data.substanceList.length) ? data.substanceList.some((el) => { return el !== null }) : false
            let blendsHere = (data.blendList && data.blendList.length) ? data.blendList.some((el) => { return el !== null }) : false

            if (substancesHere) {
                for (let substance of data.substanceList) {
                    if(!data.prefill){
                        context.commit('incrementOrderingId',{tabName:data.currentSectionName})
                    }
                    let ordering_id = context.state.form.tabs[data.currentSectionName].ordering_id
                    let inner_fields = tableRowConstructor.getInnerFields(data.currentSectionName, substance, data.groupName, data.country, null, data.prefillData, ordering_id)
                    context.commit('addSubstance', { sectionName: data.currentSectionName, row: inner_fields })
                }
            } else if (blendsHere) {
                for (let blend of data.blendList) {
                    if(!data.prefill) {
                        context.commit('incrementOrderingId',{tabName:data.currentSectionName})
                    }
                    let ordering_id = context.state.form.tabs[data.currentSectionName].ordering_id
                    let inner_fields = tableRowConstructor.getInnerFields(data.currentSectionName, null, data.groupName, data.country, blend, data.prefillData, ordering_id)
                    context.commit('addSubstance', { sectionName: data.currentSectionName, row: inner_fields })
                }
            }
        },

        prefillEmissionsRow(context, data) {
            let row = {
                id: {
                    selected: null,
                },
                ordering_id: {
                    selected: 0,
                },
                facility_name: {
                    type: 'text',
                    selected: '',
                },
                quantity_generated: {
                    type: 'number',
                    selected: '',
                },
                quantity_feedstock: {
                    type: 'number',
                    selected: '',
                },
                quantity_destroyed: {
                    type: 'number',
                    selected: '',
                },
                quantity_emitted: {
                    type: 'number',
                    selected: '',
                },
                remarks_party: {
                    type: 'textarea',
                    selected: '',
                },
                remarks_os: {
                    type: 'textarea',
                    selected: '',
                },
                get validation() {
                    let errors = []
                    if (!this.facility_name.selected) {
                        errors.push('eroare1')
                    }

                    let returnObj = {
                        type: 'nonInput',
                        selected: errors
                    }

                    return returnObj
                },
            }
            if (data) {
                Object.keys(data).forEach((element, index) => {
                    console.log(element)
                    row[element].selected = data[element]
                });
            }
            context.commit('addEmissionsRow', row)
        },

        removeDataFromTab(context, data) {
            return new Promise((resolve, reject) => {
                context.commit('resetTab', data)
                resolve()
            });
        }
    },

    mutations: {
            // data - {value:value, fieldInfo:{index:tab_info.form_fields.indexOf(row),tabName: tabName, field:order}}
        updateFormField(state,data){
            let path;
            data.fieldInfo.index === data.fieldInfo.field 
            ?
            state.form.tabs[data.fieldInfo.tabName].form_fields[data.fieldInfo.index].selected = data.value
            :
            state.form.tabs[data.fieldInfo.tabName].form_fields[data.fieldInfo.index][data.fieldInfo.field].selected = data.value 
        },


        getEmptyForm(state){
            state.form = JSON.parse(JSON.stringify(state.baseForm))
        },


        incrementOrderingId(state,data){
            state.form.tabs[data.tabName].ordering_id += 1 
        },
    

        setTabOrderingId(state,data){
            console.log(data.tabName)
            state.form.tabs[data.tabName].ordering_id = data.ordering_id 
        },

        // dashboard

        setDashboardParties(state, data) {
            state.dashboard.parties = data
        },
        setDashboardObligations(state, data) {
            state.dashboard.obligations = data
        },
        setDashboardPeriods(state, data) {
            state.dashboard.periods = data
        },
        setDashboardSubmissions(state, data) {
            state.dashboard.submissions = data
        },


        // alerts

        setCurrentAlertMessage(state, message) {
            state.currentAlert.message = message
        },

        setCurrentAlertVisibility(state, showState) {
            state.currentAlert.show = showState
        },

        setCurrentAlertVariant(state, variant) {
            state.currentAlert.variant = variant
        },

        // initial data

        updateAvailableTransitions(state, data) {
            state.available_transitions = data
        },

        updateSubmissionData(state, data) {
            state.current_submission = data
        },

        updateCountries(state, data) {
            state.initialData.countryOptions = data
        },

        updateCountriesDisplay(state, data) {
            state.initialData.display.countries = data
        },

        updateSubstances(state, data) {
            state.initialData.substances = data
        },

        updateSubstancesDisplay(state, data) {
            state.initialData.display.substances = data
        },


        updateBlends(state, data) {
            state.initialData.blends = data
        },

        updateBlendsDisplay(state, data) {
            state.initialData.display.blends = data
        },


        // questionaire
        updateQuestionaireField(state, data) {
            let currentField = store.state.form.tabs.questionaire_questions.form_fields[data.field]
            currentField && (currentField.selected = data.value)
        },

        // addsubstance
        addSubstance(state, data) {
            store.state.form.tabs[data.sectionName].form_fields.push(data.row)
        },

        addEmissionsRow(state, data) {
            store.state.form.tabs.has_emissions.form_fields.push(data)
        },

        addCreateBlendToBlendList(state, data) {
            store.state.initialData.blends.push(data)
        },

        setTabStatus(state, data) {
            store.state.form.tabs[data.tab].status = data.value
        },

        // permissions
        updateDashboardPermissions(state, permission) {
            state.permissions.dashboard = permission
        },
        updateFormPermissions(state, permission) {
            state.permissions.form = permission
        },
        updateActionsPermissions(state, permission) {
            state.permissions.actions = permission
        },

        // form state
        updateNewTabs(state, tab) {
            state.newTabs.push(tab)
        },

        tabHasBeenSaved(state, tab) {
            state.newTabs = state.newTabs.filter( currentTab => currentTab !== tab)
        },

        // removal

        resetTab(state, tab) {
            state.form.tabs[tab].form_fields = []
        },

        removeField(state, data) {
            state.form.tabs[data.tab].form_fields.splice(data.index, 1)
        }
    }
})


export default store