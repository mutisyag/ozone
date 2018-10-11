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
      <b-btn variant="outline-success">
        Save
      </b-btn>
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
            <subinfo :info="data.tabs.sub_info" :tabId="-1"></subinfo>
          </b-tab>
          <b-tab title="Questionaire" active>
            <intro tabId="0" :tabs="display_tabs" :info="data.tabs.tab_1"></intro>
          </b-tab>
          <b-tab :disabled="!display_tabs[data.tabs.tab_2.name]" :title="data.tabs.tab_2.title">
            <tab2 tabId="1" :info="data.tabs.tab_2"></tab2>
          </b-tab>
          <b-tab :disabled="!display_tabs[data.tabs.tab_3.name]" :title="data.tabs.tab_3.title">
            <tab3 tabId="2" :info="data.tabs.tab_3"></tab3>
          </b-tab>
          <b-tab :disabled="!display_tabs[data.tabs.tab_4.name]" :title="data.tabs.tab_4.title">
            <tab4 tabId="3" :info="data.tabs.tab_4"></tab4>
          </b-tab>
          <b-tab :disabled="!display_tabs[data.tabs.tab_5.name]" :title="data.tabs.tab_5.title">
            <tab5 tabId="4" :info="data.tabs.tab_5"></tab5>
          </b-tab>
          <b-tab :disabled="!display_tabs[data.tabs.tab_6.name]" :title="data.tabs.tab_6.title">
            <tab6 tabId="5" :info="data.tabs.tab_6"></tab6>
          </b-tab>
           <b-tab title="Attachements">
            <attachements :info="data.tabs.attachements" tabId="6"></attachements>
          </b-tab>
        </b-tabs>
        <!-- <formsubmit :country="country" :info="form"></formsubmit> -->
      </b-form>
    </b-card>
  <!--   <div v-if="!prefilled" class="spinner">
      <div class="loader"></div>
    </div> -->
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
import Tab1 from "./Tab1.vue";
import Tab2 from "./Tab2.vue";
import Tab3 from "./Tab3.vue";
import Tab4 from "./Tab4.vue";
import Tab5 from "./Tab5.vue";
import Tab6 from "./Tab6.vue";
import SubmissionInfo from "./SubmissionInfo.vue";
import Attachements from "./Attachements.vue";
import {getInstructions} from '@/api/api.js'
import {Footer} from '@coreui/vue'

export default {

  name: 'TabsManager',

  components: {
    intro: Tab1,
    tab2: Tab2,
    tab3: Tab3,
    tab4: Tab4,
    tab5: Tab5,
    tab6: Tab6,
    subinfo: SubmissionInfo,
    attachements: Attachements,
    Footer
  },

  props: {
    data: null
  },

  created() {
  },

  methods: {

    createModalData() {
      getInstructions().then((response) => {
        this.modal_data = response.data
        this.$refs.instructions_modal.show()
      })
    },

  },

  data () {
    return {
      tabIndex: 0,
      modal_data: null,
      display_tabs: {
        export_question: false,
        import_question: false,
        destruction_question: false,
        nonparty_question: false,
        production_question: false
      },
      titles: [
      {title:'Submission Info'},
      {title: 'Questionaire'},
      {title:'Data on Imports'},
      {title:'<b>Data on exports</b> <br> <small>Annexes A, B, C and E substances</small> <br> <small>in metric tonnes ( not ODP tonnes)</small>', tooltip: '* Includes re exports. Ref. decisions IV/14 and XVII/16, paragraph 4.'}
      ],
      subtitles: ['', 'Respondents are requested to read the Introduction in section 2, the General Instructions in section 4 and the Definitions in section 5 carefully before proceeding to the questionnaire and to refer to them as necessary when completing the data forms.','', 'Fill in this form only if your country exported or re-exported CFCs, HCFCs, HBFCs, halons, methyl chloroform, carbon tetrachloride, bromochloromethane, or methyl bromide']
    }
  },

  watch: {
      tabIndex: {
        handler: function(new_val, old_val) {
          var body = document.querySelector('body')
          console.log(new_val)
          if([2,3,4,5].includes(new_val)) {
            body.classList.add('aside-menu-lg-show')
          } else {
            body.classList.remove('aside-menu-lg-show')
          }
        }
      }
    },
}


</script>

<style lang="css" scoped>

.spinner {
    z-index: 1;
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(0,0,0,0.2);
    display: flex;
    justify-content: center;
    align-items: center;
}

.loader {
  border: 16px solid #f3f3f3;
  border-radius: 50%;
   border-top: 16px solid blue;
   border-right: 16px solid green;
   border-bottom: 16px solid red;
   border-left: 16px solid pink;
  width: 120px;
  height: 120px;
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