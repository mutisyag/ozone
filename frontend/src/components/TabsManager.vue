<template>
  <div>
  <div class="breadcrumb custom">
    <small style="width: 30%;">
      <b-btn style="margin-right:.5rem" variant="info-outline" @click="createModalData"> <i class="fa fa-info fa-lg"></i></b-btn>
      <div v-html="subtitles[tabIndex]"></div>
    </small>
    <div class="tab-title">
      <div  v-if='titles[tabIndex].tooltip' v-b-tooltip :title="titles[tabIndex].tooltip" >
        <span v-html="titles[tabIndex].title"></span>
         <i style='margin-left: 5px' class="fa fa-info-circle fa-lg"></i>
      </div>
      <div v-else v-html="titles[tabIndex].title"></div>
    </div>
    <b-button-group class="actions">
      <Save :submit.sync="saveForSubmit"  v-if="$store.state.available_transitions.includes('submit')"  :data="$store.state.form" :submission="submission"></Save>
      <b-btn  
        v-if="$store.state.available_transitions.includes('submit')" 
       @click="checkBeforeSubmitting" 
       variant="outline-success"
       >
        Submit
      </b-btn>
      <b-btn v-if="$store.state.available_transitions.includes('recall')" @click="$store.dispatch('doSubmissionTransition', {submission:submission, transition:'recall'})"  variant="outline-warning">
        Recall
      </b-btn>
      <b-btn v-if="$store.state.available_transitions.includes('process')" @click="$store.dispatch('doSubmissionTransition', {submission:submission, transition:'process'})"  variant="outline-primary">
        Process
      </b-btn>
      <b-btn v-if="$store.state.available_transitions.includes('reinstate')" @click="$store.dispatch('doSubmissionTransition', {submission:submission, transition:'reinstate'})"  variant="outline-primary">
        Reinstate
      </b-btn>
    </b-button-group>
  </div>

  <b-modal size="lg" ref="instructions_modal" id="instructions_modal">
    <div v-if="modal_data" v-html="modal_data"></div>
  </b-modal>

  <b-container style="position: relative">
    <b-card style="margin-bottom: 5rem;" no-body>
        <b-tabs v-model="tabIndex" card>

          <b-tab title="Submission Info">
             <template slot="title">
              <div class="tab-title">
                Submission Info
              </div>
             </template>
            <subinfo ref="sub_info" :info="$store.state.form.tabs.sub_info" :tabId="0"></subinfo>
          </b-tab>

          <b-tab title="Questionaire" active>
            <template slot="title">
              <div class="tab-title">
                {{$store.state.form.tabs.questionaire_questions.title}}
                <div v-if="$store.state.form.tabs.questionaire_questions.status === 'saving'" class="spinner">
                  <div class="loader"></div>
                </div>
                <i v-if="$store.state.form.tabs.questionaire_questions.status === false" style="color: red;" class="fa fa-times-circle fa-lg"></i>
                <i v-if="$store.state.form.tabs.questionaire_questions.status === true" style="color: green;" class="fa fa-check-circle fa-lg"></i>
                <i v-if="$store.state.form.tabs.questionaire_questions.status === 'edited'" class="fa fa-edit fa-lg"></i>
              </div>
             </template>
            <intro tabId="1" :info="$store.state.form.tabs.questionaire_questions"></intro>
          </b-tab>

          <b-tab v-for="tab in tabs" :title-link-class="$store.state.form.tabs[tab].status ? {} : null"  :key="tab" :disabled="!display_tabs[$store.state.form.tabs[tab].name]">
             <template slot="title">
              <div class="tab-title">
                {{$store.state.form.tabs[tab].title}}
                <div v-if="$store.state.form.tabs[tab].status === 'saving'" class="spinner">
                  <div class="loader"></div>
                </div>
                <i v-if="$store.state.form.tabs[tab].status === false" style="color: red;" class="fa fa-times-circle fa-lg"></i>
                <i v-if="$store.state.form.tabs[tab].status === true" style="color: green;" class="fa fa-check-circle fa-lg"></i>
                <i v-if="$store.state.form.tabs[tab].status === 'edited'" class="fa fa-edit fa-lg"></i>
              </div>
             </template>
            <formtemplate :tabId="tabs.indexOf(tab) + 2" :ref="tab" :tabIndex="tabIndex" :tabName="tab"></formtemplate>
          </b-tab>

          <b-tab :title-link-class="$store.state.form.tabs.has_emissions.title ? {} : null" :disabled="!display_tabs[$store.state.form.tabs.has_emissions.name]">
            <template slot="title">
              <div class="tab-title">
                {{$store.state.form.tabs.has_emissions.title}}
                <div v-if="$store.state.form.tabs.has_emissions.status === 'saving'" class="spinner">
                  <div class="loader"></div>
                </div>
                <i v-if="$store.state.form.tabs.has_emissions.status === false" style="color: red;" class="fa fa-times-circle fa-lg"></i>
                <i v-if="$store.state.form.tabs.has_emissions.status === true" style="color: green;" class="fa fa-check-circle fa-lg"></i>
                <i v-if="$store.state.form.tabs.has_emissions.status === 'edited'" class="fa fa-edit fa-lg"></i>

              </div>
             </template>
            <emissionstemplate tabId="7" ref="has_emissions"  :tabIndex="tabIndex"   tabName="has_emissions"></emissionstemplate>
          </b-tab>

           <b-tab title="Attachments">
            <attachments tabId="8"></attachments>
          </b-tab>
        </b-tabs>
        <!-- <formsubmit :country="country" :info="form"></formsubmit> -->

        <div class="legend">
            <b>Legend:</b>
            <div>
              <div class="spinner">
                <div class="loader"></div>
              </div> - Form is curently being saved
            </div>
            <div>
              <i style="color: red;" class="fa fa-times-circle fa-lg"></i> - Form save failed. Please check the validation
            </div>
            <div>
              <i style="color: green;" class="fa fa-check-circle fa-lg"></i> - Form was saved or no modifications were made. Current form data is synced with the data on the server
            </div>
            <div>
              <i class="fa fa-edit fa-lg"></i> - The form was edited and the data is not yet saved on the server. Please save before closing the form
            </div>
        </div>
    </b-card>
    </b-container>
    <Footer>
      <b-button-group class="actions mt-2 mb-2">
        <Save v-if="$store.state.available_transitions.includes('submit')" :data="$store.state.form" :submission="submission"></Save>
        <b-btn  
          v-if="$store.state.available_transitions.includes('submit')"  
          @click="checkBeforeSubmitting" 
          variant="outline-success"
          >
            Submit
          </b-btn>
          <b-btn v-if="$store.state.available_transitions.includes('recall')" @click="$store.dispatch('doSubmissionTransition', {submission:submission, transition:'recall'})"  variant="outline-warning">
            Recall
          </b-btn>
          <b-btn v-if="$store.state.available_transitions.includes('process')" @click="$store.dispatch('doSubmissionTransition', {submission:submission, transition:'process'})"  variant="outline-primary">
            Process
          </b-btn>
          <b-btn v-if="$store.state.available_transitions.includes('reinstate')" @click="$store.dispatch('doSubmissionTransition', {submission:submission, transition:'reinstate'})"  variant="outline-primary">
            Reinstate
        </b-btn>
        <b-btn @click="$refs.history_modal.show()" variant="outline-info">
          Versions
        </b-btn>
        <b-btn @click="removeSubmission" v-if="$store.state.available_transitions.includes('submit')"  variant="outline-danger">
          Delete Submission
        </b-btn>
      </b-button-group>
    </Footer>

    <b-modal size="lg" ref="history_modal" id="history_modal">
        <SubmissionHistory :history="$store.state.currentSubmissionHistory"></SubmissionHistory>
    </b-modal>
  </div>
</template>

<script>
import { Footer } from '@coreui/vue'
import Questionnaire from './Questionnaire.vue'
import FormTemplate from './FormTemplateNew.vue'
import EmissionsTemplate from './EmissionsTemplate.vue'
import SubmissionInfo from './SubmissionInfo.vue'
import Attachments from './Attachments.vue'
import { getInstructions } from '@/api/api.js'
import Save from './Save'
import SubmissionHistory from './SubmissionHistory.vue'

export default {

	name: 'TabsManager',

	components: {
		intro: Questionnaire,
		formtemplate: FormTemplate,
		emissionstemplate: EmissionsTemplate,
		subinfo: SubmissionInfo,
		attachments: Attachments,
		Footer,
		Save,
		SubmissionHistory
	},

	props: {
		data: null,
		submission: String
	},

	created() {
	},

	computed: {
		display_tabs() {
			const questionaire_tab = this.$store.state.form.tabs.questionaire_questions.form_fields
			return {
				has_exports: questionaire_tab.has_exports.selected,
				has_imports: questionaire_tab.has_imports.selected,
				has_destroyed: questionaire_tab.has_destroyed.selected,
				has_nonparty: questionaire_tab.has_nonparty.selected,
				has_produced: questionaire_tab.has_produced.selected,
				has_emissions: questionaire_tab.has_emissions.selected
			}
		}
	},

	methods: {
		createModalData() {
			getInstructions().then((response) => {
				this.modal_data = response.data
				this.$refs.instructions_modal.show()
      })
    },
      
    checkBeforeSubmitting() {
      let fields = Object.keys(this.$store.state.form.tabs)
      .filter(tab =>  !['questionaire_questions', 'sub_info','attachments'].includes(tab) )
      .map(tab => {return this.$store.state.form.tabs[tab].form_fields})
      .filter( arr => arr.length)
      if(!fields.length) {
        this.$store.dispatch('setAlert', { message: "You cannot submit and empty form",variant: 'danger' })		       
        return
      }
        this.saveForSubmit = true
      },

		removeSubmission() {
			const r = confirm('Deleting the submission is ireversible. Are you sure ?')
			if (r === true) {
				this.$store.dispatch('removeSubmission', this.submission).then(() => {
					this.$router.push({ name: 'Dashboard' })
				})
			}
		}

	},

	data() {
		return {
			tabIndex: 0,
      modal_data: null,
      saveForSubmit: false,
			tabs: ['has_imports', 'has_exports', 'has_produced', 'has_destroyed', 'has_nonparty'],
			titles: [
				{ title: 'Submission Info' },
				{ title: 'Questionaire' },
				{ title: '<b>IMPORTS</b> <br> <small>Annexes A, B, C and E substances</small> <br> <small>in metric tonnes ( not ODP tonnes)</small>' },
				{
					title: '<b>EXPORTS</b> <br> <small>Annexes A, B, C and E substances</small> <br> <small>in metric tonnes ( not ODP tonnes)</small>',
					tooltip: '* Includes re exports. Ref. decisions IV/14 and XVII/16, paragraph 4.'
				},
				{ title: '<b>PRODUCTION </b> <br><small> in tonnes (not ODP or GWP tonnes)<br>Annex A, B, C, E and F substances  </small>' },
				{ title: '<b>QUANTITY OF SUBSTANCES DESTROYED </b> <br><small> in tonnes (not ODP or GWP tonnes)<br>Annex A, B, C, E and F substances  </small>' },
				{
					title: '<b>IMPORTS FROM AND/OR EXPORTS TO NON PARTIES* </b> <br><small> in tonnes (not ODP or GWP tonnes)<br>Annex A, B, C and E substances  </small>',
					tooltip: '* See definition of “non parties” in Instruction V.'
				},
				{ title: '<b>EMISSIONS</b> <br> <small> in tonnes[1] (not ODP or GWP tonnes)</small>' },
				{ title: 'Attachments' }
			],
			subtitles: ['',
				'Respondents are requested to read the Introduction in section 2, the General Instructions in section 4 and the Definitions in section 5 carefully before proceeding to the questionnaire and to refer to them as necessary when completing the data forms.',
				'Fill in this form only if your country imported CFCs, halons, carbon tetrachloride, methyl chloroform, HCFCs, HBFCs, bromochloromethane, methyl bromide or HFCs',
				'Fill in this form only if your country exported or re-exported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide',
				'Fill in this form only if your country produced CFCs, halons, carbon tetrachloride, methyl chloroform, HCFCs, HBFCs, bromochloromethane, methyl bromide or HFCs',
				'Fill in this form only if your country destroyed CFCs, halons, carbon tetrachloride, methyl chloroform, HCFCs, HBFCs, bromochloromethane, methyl bromide or HFCs',
				'Fill in this form only if your country imported or exported CFCs, halons, carbon tetrachloride, methyl chloroform, HCFCs, HBFCs, bromochloromethane or methyl bromide to non parties ',
				'Fill in this form only if your country generated HFC 23 from any facility that produced (manufactured) Annex C Group I or Annex F substances '
			]
		}
	},

	watch: {
		tabIndex: {
			handler(new_val) {
				const body = document.querySelector('body')
				if ([2, 3, 4, 5, 6].includes(new_val) && !this.$store.getters.transitionState) {
					body.classList.add('aside-menu-lg-show')
				} else {
					body.classList.remove('aside-menu-lg-show')
				}
			}
		}
	}
}

</script>

<style lang="css" scoped>
.legend {
  padding: .2rem 2rem;
  background: #f0f3f5;
}

.legend .spinner {
  margin-left: 0;
}

.tab-title {
  display: flex;
}

.tab-title i {
  margin-left: 5px;
}

.spinner {
    z-index: 1;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    margin-left: 5px;
}

.loader {
  border: 3px solid #f3f3f3;
  border-radius: 50%;
   border-top: 3px solid blue;
   border-right: 3px solid green;
   border-bottom: 3px solid red;
   border-left: 3px solid pink;
  width: 15px;
  height: 15px;
  -webkit-animation: spin 2s linear infinite; /* Safari */
  animation: spin 2s linear infinite;
}

/* Safari */
@-webkit-keyframes spin {
  0% { -webkit-transform: rotate(0deg); }
  100% { -webkit-transform: rotate(360deg); }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
