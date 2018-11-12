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
      <Save v-on:tabStatusChange="updateTabStatus" v-if="submission && data" :data="data.form" :submission="submission"></Save>
      <b-btn variant="success">
        Submit
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
            <subinfo ref="sub_info" :info="data.form.tabs.sub_info" :tabId="-1"></subinfo>
          </b-tab>
          <b-tab title="Questionaire" active>
            <intro tabId="0" :tabs="display_tabs" :info="data.form.tabs.tab_1"></intro>
          </b-tab>
          <b-tab :title-link-class="data.form.tabs.tab_2.title ? {} : null" :disabled="!display_tabs[data.form.tabs.tab_2.name]">
            <template slot="title">
               <div class="tab-title">
                {{data.form.tabs.tab_2.title}}
                <div v-if="tabStatus.has_imports === 'saving'" class="spinner">
                  <div class="loader"></div>
                </div>
                <span v-else>
                  <i v-if="tabStatus.has_imports === false" style="color: red;" class="fa fa-times-circle fa-lg"></i>
                  <i v-if="tabStatus.has_imports === true" style="color: green;" class="fa fa-check-circle fa-lg"></i>
                </span>
              </div>
             </template>
            <formtemplate ref="tab_2" tabId="1"  :data="{substances: data.substances, countryOptions: data.countryOptions, blends: data.blends}"  :structure="data.form.tabs.tab_2"></formtemplate>
          </b-tab>


          <b-tab :title-link-class="data.form.tabs.tab_3.title ? {} : null"  :disabled="!display_tabs[data.form.tabs.tab_3.name]">
             <template slot="title">
              <div class="tab-title">
                {{data.form.tabs.tab_3.title}}
                <div v-if="tabStatus.has_exports === 'saving'" class="spinner">
                  <div class="loader"></div>
                </div>
                <span v-else>
                  <i v-if="tabStatus.has_exports === false" style="color: red;" class="fa fa-times-circle fa-lg"></i>
                  <i v-if="tabStatus.has_exports === true" style="color: green;" class="fa fa-check-circle fa-lg"></i>
                </span>
              </div>

             </template>
            <formtemplate tabId="2" ref="tab_3" :data="{substances: data.substances, countryOptions: data.countryOptions, blends: data.blends}"  :structure="data.form.tabs.tab_3"></formtemplate>
          </b-tab>

          
         <b-tab :title-link-class="data.form.tabs.tab_3.title ? {} : null" :disabled="!display_tabs[data.form.tabs.tab_4.name]">
             <template slot="title">
              <div class="tab-title">
                {{data.form.tabs.tab_4.title}}
                <div v-if="tabStatus.has_produced === 'saving'" class="spinner">
                   <div class="loader"></div>
                </div>
                <span v-else>
                  <i v-if="tabStatus.has_produced === false" style="color: red;" class="fa fa-times-circle fa-lg"></i>
                  <i v-if="tabStatus.has_produced === true" style="color: green;" class="fa fa-check-circle fa-lg"></i>
                </span>
              </div>
             </template>
            <formtemplate tabId="3"  ref="tab_4" :data="{substances: data.substances, countryOptions: data.countryOptions, blends: data.blends}"  :structure="data.form.tabs.tab_4"></formtemplate>
          </b-tab>

          <b-tab :title-link-class="data.form.tabs.tab_4.title ? {} : null" :disabled="!display_tabs[data.form.tabs.tab_5.name]">
            <template slot="title">
              <div class="tab-title">
                {{data.form.tabs.tab_5.title}}
                <div v-if="tabStatus.has_destroyed === 'saving'" class="spinner">
                  <div class="loader"></div>
                </div>
                <span v-else>
                  <i v-if="tabStatus.has_destroyed === false" style="color: red;" class="fa fa-times-circle fa-lg"></i>
                  <i v-if="tabStatus.has_destroyed === true" style="color: green;" class="fa fa-check-circle fa-lg"></i>
                </span>
              </div>
             </template>
            <formtemplate tabId="4" ref="tab_5" :data="{substances: data.substances, countryOptions: data.countryOptions, blends: data.blends}"  :structure="data.form.tabs.tab_5"></formtemplate>
          </b-tab>

          <b-tab :title-link-class="data.form.tabs.tab_5.title ? {} : null" :disabled="!display_tabs[data.form.tabs.tab_6.name]">
            <template slot="title">
              <div class="tab-title">
                {{data.form.tabs.tab_6.title}}
                <div v-if="tabStatus.has_nonparty === 'saving'" class="spinner">
                  <div class="loader"></div>
                </div>
                <span v-else>
                  <i v-if="tabStatus.has_nonparty === false" style="color: red;" class="fa fa-times-circle fa-lg"></i>
                  <i v-if="tabStatus.has_nonparty === true" style="color: green;" class="fa fa-check-circle fa-lg"></i>
                </span>
              </div>
             </template>
            <formtemplate tabId="5" ref="tab_6" :data="{substances: data.substances, countryOptions: data.countryOptions, blends: data.blends}"  :structure="data.form.tabs.tab_6"></formtemplate>
          </b-tab>
           <b-tab :title-link-class="data.form.tabs.tab_5.title ? {} : null" :disabled="!display_tabs[data.form.tabs.tab_7.name]">
            <template slot="title">
              <div class="tab-title">
                {{data.form.tabs.tab_7.title}}
                <div v-if="tabStatus.has_emissions === 'saving'" class="spinner">
                  <div class="loader"></div>
                </div>
                <span v-else>
                  <i v-if="tabStatus.has_emissions === false" style="color: red;" class="fa fa-times-circle fa-lg"></i>
                  <i v-if="tabStatus.has_emissions === true" style="color: green;" class="fa fa-check-circle fa-lg"></i>
                </span>
              </div>
             </template>
            <emissionstemplate tabId="6" ref="tab_7" :data="{substances: data.substances, countryOptions: data.countryOptions, blends: data.blends}"  :structure="data.form.tabs.tab_7"></emissionstemplate>
          </b-tab>
           <b-tab title="Attachements">
            <attachements :info="data.form.tabs.attachements" tabId="6"></attachements>
          </b-tab> 
        </b-tabs>
        <!-- <formsubmit :country="country" :info="form"></formsubmit> -->
      </b-form>
    </b-card>
    </b-container>
    <Footer>
      <b-button-group class="actions mt-2 mb-2">
        <b-btn variant="info">
          Versions
        </b-btn>
        <b-btn variant="danger">
          Delete Submission
        </b-btn>
        <b-btn variant="primary">
          Save
        </b-btn>
        <b-btn variant="success">
          Submit
        </b-btn>
      </b-button-group>
    </Footer>
  </div>
</template>

<script>
import PartyInfo from "./PartyInfo.vue";
import FormTemplate from "./FormTemplate.vue";
import EmissionsTemplate from "./EmissionsTemplate.vue";
import SubmissionInfo from "./SubmissionInfo.vue";
import Attachements from "./Attachements.vue";
import {getInstructions, getUsers} from '@/api/api.js'
import {Footer} from '@coreui/vue'
import Save from './Save'
export default {

  name: 'TabsManager',

  components: {
    intro: PartyInfo,
    formtemplate: FormTemplate,
    emissionstemplate: EmissionsTemplate,
    subinfo: SubmissionInfo,
    attachements: Attachements,
    Footer,
    Save
  },

  props: {
    data: null,
    submission: Object,
  },

  created() {
    this.data.form.tabs.sub_info.party.selected = this.submission.party
    this.data.form.tabs.sub_info.reporting_year.selected = this.submission.reporting_period
  },



  computed: {

    getValidatorValues(){
      console.log(this.$validator._base.errors.items)
      return this.$validator._base.errors.items
    },
  },

  methods: {

  updateTabStatus(val) {
    console.log(val)
    this.tabStatus[val[0]] = val[1]
  },

    createModalData() {
      getInstructions().then((response) => {
        this.modal_data = response.data
        this.$refs.instructions_modal.show()
      })
    },


    getValidationStatus(tab_name){
     this.$nextTick( () => {

      let validationTabContent = this.$refs[tab_name]
      let tabIsInvalid = validationTabContent ? validationTabContent.$children.find( child => {return child.$refs.invalid}) : null
      if(tabIsInvalid) {
        this.data.form.tabs[tab_name].isInvalid = true
      }
      else {
        this.data.form.tabs[tab_name].isInvalid = false
      }
      this.$nextTick().then(() => {
       this.$forceUpdate()
      })
     })
    },

  },

  data () {
    return {
      tabStatus : {
        has_imports: '',
        has_exports: '',
        has_produced: '',
        has_destroyed: '',
        has_nonparty: '',
        has_emissions: '',
      },
      tabIndex: 0,
      modal_data: null,
      display_tabs: {
        has_exports: false,
        has_imports: false,
        has_destroyed: false,
        has_nonparty: false,
        has_produced: false,
        has_emissions: false,
      },
      titles: [
      {title:'Submission Info'},
      {title: 'Questionaire'},
      {title:'<b>Data on Imports</b>'},
      {title:'<b>Data on exports</b> <br> <small>Annexes A, B, C and E substances</small> <br> <small>in metric tonnes ( not ODP tonnes)</small>', tooltip: '* Includes re exports. Ref. decisions IV/14 and XVII/16, paragraph 4.'},
      {title:'<b> Data on production </b>'},
      {title:'<b> Data on Destruction </b>'},
      {title:'<b> Data on Non-party </b>'},
      {title:'<b> Data on Emissions </b>'},
      ],
      subtitles: ['', 'Respondents are requested to read the Introduction in section 2, the General Instructions in section 4 and the Definitions in section 5 carefully before proceeding to the questionnaire and to refer to them as necessary when completing the data forms.','', 'Fill in this form only if your country exported or re-exported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide']
    }
  },

  watch: {
      tabIndex: {
        handler: function(new_val, old_val) {
          var body = document.querySelector('body')
          if([2,3,4,5,6].includes(new_val)) {
            body.classList.add('aside-menu-lg-show')
          } else {
            body.classList.remove('aside-menu-lg-show')
          }
        }
      },
      getValidatorValues: {
       handler: function(val) {
        if(this.data.form){
          for(let tab in this.data.form.tabs) {
              this.getValidationStatus(tab)
          }
        }
      },
      deep: true

    },
  }
}


</script>

<style lang="css" scoped>
.tab-title {
  display: flex;
}

.tab-title i {
  margin-left: 5px;
}

.spinner {
    z-index: 1;
    display: flex;
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