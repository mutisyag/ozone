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
      <Save  v-if="$store.state.available_transitions.includes('submit')"  :data="$store.state.form" :submission="submission"></Save>
      <b-btn  v-if="$store.state.available_transitions.includes('submit')"  @click="$store.dispatch('doSubmissionTransition', {submission:submission, transition:'submit'})" variant="outline-success">
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
      <b-form>

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
            <intro tabId="1" :info="$store.state.form.tabs.questionaire_questions"></intro>
          </b-tab>
         

          <b-tab :title-link-class="$store.state.form.tabs.has_imports.status ? {} : null"  :disabled="!display_tabs[$store.state.form.tabs.has_imports.name]">
             <template slot="title">
              <div class="tab-title">
                {{$store.state.form.tabs.has_imports.title}}
                <div v-if="$store.state.form.tabs.has_imports.status === 'saving'" class="spinner">
                  <div class="loader"></div>
                </div>
                <i v-if="$store.state.form.tabs.has_imports.status === false" style="color: red;" class="fa fa-times-circle fa-lg"></i>
                <i v-if="$store.state.form.tabs.has_imports.status === true" style="color: green;" class="fa fa-check-circle fa-lg"></i>
                <i v-if="$store.state.form.tabs.has_imports.status === 'edited'" class="fa fa-edit fa-lg"></i>
              
              </div>

             </template>
            <formtemplate tabId="2" ref="has_imports" :tabIndex="tabIndex" tabName="has_imports"></formtemplate>
          </b-tab>

          <b-tab :title-link-class="$store.state.form.tabs.has_exports.status ? {} : null" :disabled="!display_tabs[$store.state.form.tabs.has_exports.name]">
            <template slot="title">
               <div class="tab-title">
                {{$store.state.form.tabs.has_exports.title}}
                <div v-if="$store.state.form.tabs.has_exports.status === 'saving'" class="spinner">
                  <div class="loader"></div>
                </div>
                <i v-if="$store.state.form.tabs.has_exports.status === false" style="color: red;" class="fa fa-times-circle fa-lg"></i>
                <i v-if="$store.state.form.tabs.has_exports.status === true" style="color: green;" class="fa fa-check-circle fa-lg"></i>
                <i v-if="$store.state.form.tabs.has_exports.status === 'edited'" class="fa fa-edit fa-lg"></i>
              </div>
             </template>
            <formtemplate ref="has_exports" tabId="3" :tabIndex="tabIndex"  tabName="has_exports"></formtemplate>
          </b-tab>


         <b-tab :title-link-class="$store.state.form.tabs.has_produced.title ? {} : null" :disabled="!display_tabs[$store.state.form.tabs.has_produced.name]">
             <template slot="title">
              <div class="tab-title">
                {{$store.state.form.tabs.has_produced.title}}
                <div v-if="$store.state.form.tabs.has_produced.status === 'saving'" class="spinner">
                   <div class="loader"></div>
                </div>
                <i v-if="$store.state.form.tabs.has_produced.status === false" style="color: red;" class="fa fa-times-circle fa-lg"></i>
                <i v-if="$store.state.form.tabs.has_produced.status === true" style="color: green;" class="fa fa-check-circle fa-lg"></i>
                <i v-if="$store.state.form.tabs.has_produced.status === 'edited'" class="fa fa-edit fa-lg"></i>
              
              </div>
             </template>
            <formtemplate tabId="4"  ref="has_produced"  :tabIndex="tabIndex"   tabName="has_produced"></formtemplate>
          </b-tab>

          <b-tab :title-link-class="$store.state.form.tabs.has_destroyed.title ? {} : null" :disabled="!display_tabs[$store.state.form.tabs.has_destroyed.name]">
            <template slot="title">
              <div class="tab-title">
                {{$store.state.form.tabs.has_destroyed.title}}
                <div v-if="$store.state.form.tabs.has_destroyed.status === 'saving'" class="spinner">
                  <div class="loader"></div>
                </div>
                <i v-if="$store.state.form.tabs.has_destroyed.status === false" style="color: red;" class="fa fa-times-circle fa-lg"></i>
                <i v-if="$store.state.form.tabs.has_destroyed.status === true" style="color: green;" class="fa fa-check-circle fa-lg"></i>
                <i v-if="$store.state.form.tabs.has_destroyed.status === 'edited'" class="fa fa-edit fa-lg"></i>
              
              </div>
             </template>
            <formtemplate tabId="5" :tabIndex="tabIndex" ref="has_destroyed"  tabName="has_destroyed"></formtemplate>
          </b-tab>

          <b-tab :title-link-class="$store.state.form.tabs.has_nonparty.title ? {} : null" :disabled="!display_tabs[$store.state.form.tabs.has_nonparty.name]">
            <template slot="title">
              <div class="tab-title">
                {{$store.state.form.tabs.has_nonparty.title}}
                <div v-if="$store.state.form.tabs.has_nonparty.status === 'saving'" class="spinner">
                  <div class="loader"></div>
                </div>
                <i v-if="$store.state.form.tabs.has_nonparty.status === false" style="color: red;" class="fa fa-times-circle fa-lg"></i>
                <i v-if="$store.state.form.tabs.has_nonparty.status === true" style="color: green;" class="fa fa-check-circle fa-lg"></i>
                <i v-if="$store.state.form.tabs.has_nonparty.status === 'edited'" class="fa fa-edit fa-lg"></i>
              
              </div>
             </template>
            <formtemplate tabId="6" ref="has_nonparty"  :tabIndex="tabIndex"   tabName="has_nonparty"></formtemplate>
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


      </b-form>
    </b-card>
    </b-container>
    <Footer>
      <b-button-group class="actions mt-2 mb-2">
        <Save v-if="$store.state.available_transitions.includes('submit')" :data="$store.state.form" :submission="submission"></Save>
        <b-btn  v-if="$store.state.available_transitions.includes('submit')"  @click="$store.dispatch('doSubmissionTransition', {submission:submission, transition:'submit'})" variant="outline-success">
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
import Questionnaire from "./Questionnaire.vue";
import FormTemplate from "./FormTemplate.vue";
import EmissionsTemplate from "./EmissionsTemplate.vue";
import SubmissionInfo from "./SubmissionInfo.vue";
import Attachments from "./Attachments.vue";
import {getInstructions, getUsers} from '@/api/api.js'
import {Footer} from '@coreui/vue'
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
    submission: String,
  },

  created() {
  },

  computed: {
     display_tabs() {
      return {
        has_exports: this.$store.state.form.tabs.questionaire_questions.form_fields.has_exports.selected,
        has_imports: this.$store.state.form.tabs.questionaire_questions.form_fields.has_imports.selected,
        has_destroyed: this.$store.state.form.tabs.questionaire_questions.form_fields.has_destroyed.selected,
        has_nonparty: this.$store.state.form.tabs.questionaire_questions.form_fields.has_nonparty.selected,
        has_produced: this.$store.state.form.tabs.questionaire_questions.form_fields.has_produced.selected,
        has_emissions: this.$store.state.form.tabs.questionaire_questions.form_fields.has_emissions.selected,
      }
    },
  },

 
  methods: {
    createModalData() {
      getInstructions().then((response) => {
        this.modal_data = response.data
        this.$refs.instructions_modal.show()
      })
    },

    removeSubmission() {

      const r = confirm("Deleting the submission is ireversible. Are you sure ?");
      if (r == true) {
        this.$store.dispatch('removeSubmission', this.submission).then( response => {
          this.$router.push({ name: 'Dashboard' });
        })
      }
    },

  },

  data () {
    return {
      tabIndex: 0,
      modal_data: null,
      titles: [
      {title:'Submission Info'},
      {title: 'Questionaire'},
      {title:'<b>DATA ON IMPORTS</b> <br> <small>Annexes A, B, C and E substances</small> <br> <small>in metric tonnes ( not ODP tonnes)</small>'},
      {title:'<b>DATA ON EXPORTS</b> <br> <small>Annexes A, B, C and E substances</small> <br> <small>in metric tonnes ( not ODP tonnes)</small>',
       tooltip: '* Includes re exports. Ref. decisions IV/14 and XVII/16, paragraph 4.'
      },
      {title:'<b> DATA ON PRODUCTION </b> <br><small> in tonnes (not ODP or GWP tonnes)<br>Annex A, B, C, E and F substances  </small>'},
      {title:'<b> DATA ON QUANTITY OF SUBSTANCES DESTROYED </b> <br><small> in tonnes (not ODP or GWP tonnes)<br>Annex A, B, C, E and F substances  </small>'},
      {title:'<b> DATA ON IMPORTS FROM AND/OR EXPORTS TO NON PARTIES* </b> <br><small> in tonnes (not ODP or GWP tonnes)<br>Annex A, B, C and E substances  </small>',
       tooltip: '* See definition of “non parties” in Instruction V.'
      },
      {title:'<b> DATA ON QUANTITY OF EMISSIONS OF HFC 23 FROM FACILITIES MANUFACTURING ANNEX C GROUP I OR ANNEX F SUBSTANCES </b> <br> <small> in tonnes[1] (not ODP or GWP tonnes)</small>'},
      {title: 'Attachments'},
      ],
      subtitles: ['',
       'Respondents are requested to read the Introduction in section 2, the General Instructions in section 4 and the Definitions in section 5 carefully before proceeding to the questionnaire and to refer to them as necessary when completing the data forms.',
       'Fill in this form only if your country imported CFCs, halons, carbon tetrachloride, methyl chloroform, HCFCs, HBFCs, bromochloromethane, methyl bromide or HFCs', 
       'Fill in this form only if your country exported or re-exported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide', 
       'Fill in this form only if your country produced CFCs, halons, carbon tetrachloride, methyl chloroform, HCFCs, HBFCs, bromochloromethane, methyl bromide or HFCs',
       'Fill in this form only if your country destroyed CFCs, halons, carbon tetrachloride, methyl chloroform, HCFCs, HBFCs, bromochloromethane, methyl bromide or HFCs',
       'Fill in this form only if your country imported or exported CFCs, halons, carbon tetrachloride, methyl chloroform, HCFCs, HBFCs, bromochloromethane or methyl bromide to non parties ',
       'Fill in this form only if your country generated HFC 23 from any facility that produced (manufactured) Annex C Group I or Annex F substances ',
       ]
    }
  },

  watch: {
      tabIndex: {
        handler: function(new_val, old_val) {
          var body = document.querySelector('body')
          if([2,3,4,5,6].includes(new_val) && !this.$store.getters.transitionState) {
            body.classList.add('aside-menu-lg-show')
          } else {
            body.classList.remove('aside-menu-lg-show')
          }
        }
      },
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