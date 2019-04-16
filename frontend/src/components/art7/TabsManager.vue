<template>
  <div>
    <div class="breadcrumb custom">
      <small style="width: 30%;">
        <b-btn
          variant="info-outline"
          @click="createModalData"
          v-show="!selectedTab.hideInfoButton"
          style="margin-right:.5rem"
        >
          <i class="fa fa-info fa-lg"></i>
        </b-btn>
        <div v-html="selectedTab.detailsHtml"></div>
      </small>
      <div class="tab-title">
        <div v-if="selectedTab.tooltipHtml" v-b-tooltip :title="selectedTab.tooltipHtml">
          <span v-html="selectedTab.titleHtml"></span>
          <i style="margin-left: 5px" class="fa fa-info-circle fa-lg"></i>
        </div>
        <div v-else v-html="selectedTab.titleHtml"></div>
      </div>
    </div>

    <b-modal size="lg" ref="instructions_modal" id="instructions_modal">
      <div v-if="modal_data" v-html="modal_data"></div>
      <div slot="modal-footer">
        <b-btn @click="$refs.instructions_modal.hide()" variant="success">
          <span v-translate>Close</span>
        </b-btn>
      </div>
    </b-modal>

    <div class="form-wrapper" style="position: relative">
      <b-card style="margin-bottom: 5rem;" no-body>
        <b-tabs v-model="tabIndex" card>
          <b-tab active>
            <template slot="title">
              <tab-title-with-loader :tab="$store.state.form.tabs.sub_info"/>
            </template>
            <SubmissionInfo
              ref="sub_info"
              :flags_info="$store.state.form.tabs.flags"
              :info="$store.state.form.tabs.sub_info"
              :tabId="0"
            />
          </b-tab>

          <b-tab>
            <template slot="title">
              <tab-title-with-loader :tab="$store.state.form.tabs.questionaire_questions"/>
            </template>
            <Questionnaire :tabId="1" :info="$store.state.form.tabs.questionaire_questions"/>
          </b-tab>

          <b-tab
            v-for="tabId in tabsIdsWithAssideMenu"
            :disabled="selectedDisplayTabs[$store.state.form.tabs[tabId].name] === null"
            :key="tabId"
          >
            <template slot="title">
              <tab-title-with-loader :tab="$store.state.form.tabs[tabId]"/>
            </template>
            <FormTemplate
              :hasDisabledFields="!selectedDisplayTabs[$store.state.form.tabs[tabId].name]"
              :tabId="$store.state.form.formDetails.tabsDisplay.indexOf(tabId)"
              :tabIndex="tabIndex"
              :tabName="tabId"
            />
          </b-tab>

          <b-tab :disabled="selectedDisplayTabs.has_emissions === null">
            <template slot="title">
              <tab-title-with-loader :tab="$store.state.form.tabs.has_emissions"/>
            </template>
            <EmissionsTemplate
              :hasDisabledFields="!selectedDisplayTabs.has_emissions"
              :tabId="7"
              ref="has_emissions"
              :tabIndex="tabIndex"
              tabName="has_emissions"
            />
          </b-tab>

          <b-tab>
            <template slot="title">
              <tab-title-with-loader :tab="$store.state.form.tabs.files"/>
            </template>
            <Files :tabId="8" :tabIndex="tabIndex"/>
          </b-tab>
        </b-tabs>
      </b-card>
    </div>
    <Footer style="display:inline">
      <Save
        class="actions mt-2 mb-2"
        v-if="$store.getters.can_save_form"
        :data="$store.state.form"
        :submission="submission"
      ></Save>
      <router-link class="btn btn-light ml-2" :to="{name: 'Dashboard'}" v-translate>Close</router-link>
      <b-button-group class="pull-right actions mt-2 mb-2">
        <AggregationsModal :submission="submission"></AggregationsModal>
        <b-btn
          v-if="$store.state.current_submission.available_transitions.includes('submit')"
          @click="checkBeforeSubmitting"
          variant="outline-success"
        >
          <span v-translate>Submit</span>
        </b-btn>
        <b-btn
          variant="outline-primary"
          v-for="transition in availableTransitions"
          :key="transition"
          @click="currentTransition = transition"
        >
          <span>{{labels[transition]}}</span>
        </b-btn>

        <b-btn
          variant="outline-primary"
          @click="clone($route.query.submission)"
          size="sm"
          v-if="$store.state.current_submission.is_cloneable"
          :disabled="$store.state.currentUser.is_read_only"
        >Revise</b-btn>
        <b-btn
          variant="outline-primary"
          @click="$store.dispatch('downloadStuff',
						{
							url: `${submission}export_pdf/`,
							fileName: `${$store.state.current_submission.obligation} - ${$store.state.initialData.display.countries[$store.state.current_submission.party]} - ${$store.state.current_submission.reporting_period}.pdf`
						})"
        >Export as PDF</b-btn>
        <b-btn @click="$refs.history_modal.show()" variant="outline-info">
          <span v-translate>Versions</span>
        </b-btn>
        <b-btn
          @click="removeSubmission"
          id="delete-button"
          v-if="$store.getters.can_edit_data"
          variant="outline-danger"
        >
          <span v-translate>Delete Submission</span>
        </b-btn>
      </b-button-group>
    </Footer>

    <b-modal
      size="lg"
      ref="history_modal"
      id="history_modal"
      :title="$gettext('Submission versions')"
    >
      <SubmissionHistory
        :history="$store.state.currentSubmissionHistory"
        :currentVersion="$store.state.current_submission.version"
      ></SubmissionHistory>
      <div slot="modal-footer">
        <b-btn @click="$refs.history_modal.hide()" variant="success">
          <span v-translate>Close</span>
        </b-btn>
      </div>
    </b-modal>
    <TransitionQuestions
      v-on:removeTransition="currentTransition = null"
      :submission="submission"
      :transition="currentTransition"
    ></TransitionQuestions>
  </div>
</template>

<script>
import { Footer } from '@coreui/vue'
import Questionnaire from '@/components/art7/Questionnaire.vue'
import FormTemplate from '@/components/art7/FormTemplate.vue'
import EmissionsTemplate from '@/components/art7/EmissionsTemplate.vue'
import SubmissionInfo from '@/components/common/SubmissionInfo.vue'
import Files from '@/components/common/Files'
import { getInstructions, cloneSubmission } from '@/components/common/services/api'
import Save from '@/components/art7/Save'
import SubmissionHistory from '@/components/common/SubmissionHistory.vue'
import { getLabels } from '@/components/art7/dataDefinitions/labels'
import TabTitleWithLoader from '@/components/common/TabTitleWithLoader'
import TransitionQuestions from '@/components/common/TransitionQuestions'
import { getAlerts } from '@/components/common/dataDefinitions/alerts'
import AggregationsModal from '@/components/common/AggregationsModal'

export default {
  components: {
    Questionnaire,
    FormTemplate,
    EmissionsTemplate,
    SubmissionInfo,
    Files,
    Footer,
    Save,
    SubmissionHistory,
    TabTitleWithLoader,
    TransitionQuestions,
    AggregationsModal
  },
  props: {
    data: null,
    submission: String
  },

  created() {
    this.updateBreadcrumbs()
  },

  computed: {
    submissionInfoLabel() {
      return this.$gettext('Submission Info')
    },
    availableTransitions() {
      return this.$store.state.current_submission.available_transitions.filter(t => t !== 'submit')
    },
    selectedDisplayTabs() {
      const questionaire_tab = this.$store.state.form.tabs.questionaire_questions.form_fields
      return {
        has_exports: questionaire_tab.has_exports.selected,
        has_imports: questionaire_tab.has_imports.selected,
        has_destroyed: questionaire_tab.has_destroyed.selected,
        has_nonparty: questionaire_tab.has_nonparty.selected,
        has_produced: questionaire_tab.has_produced.selected,
        has_emissions: questionaire_tab.has_emissions.selected
      }
    },
    selectedTab() {
      const { form } = this.$store.state
      const tab = form.tabs[form.formDetails.tabsDisplay[this.tabIndex]]
      const body = document.querySelector('body')
      if (tab.hasAssideMenu && !this.$store.getters.isReadOnly && this.selectedDisplayTabs[tab.name]) {
        body.classList.add('aside-menu-lg-show')
      } else {
        body.classList.remove('aside-menu-lg-show')
      }
      return tab
    },
    tabsIdsWithAssideMenu() {
      const { form } = this.$store.state
      return form.formDetails.tabsDisplay.filter(tabName => form.tabs[tabName].hasAssideMenu)
    }
  },
  methods: {
    clone(url) {
      cloneSubmission(url).then((response) => {
        this.$router.push({ name: this.$route.name, query: { submission: response.data.url } })
        this.$router.go(this.$router.currentRoute)
        this.$store.dispatch('setAlert', {
          $gettext: this.$gettext,
          message: { __all__: [this.alerts.clone_success] },
          variant: 'success'
        })
        this.$destroy()
      }).catch(error => {
        this.$store.dispatch('setAlert', {
          $gettext: this.$gettext,
          message: { ...error.response.data },
          variant: 'danger' })
        console.log(error)
      })
    },
    updateBreadcrumbs() {
      this.$store.commit('updateBreadcrumbs', `${this.$store.state.current_submission.reporting_period} ${this.$store.state.current_submission.obligation} ${this.$gettext('submission for')} ${this.$store.state.initialData.display.countries[this.$store.state.current_submission.party]}`)
    },
    createModalData() {
      const tabName = this.$store.state.form.formDetails.tabsDisplay[this.tabIndex]
      const formName = this.$route.name
      if (tabName) {
        getInstructions(formName, tabName).then((response) => {
          this.modal_data = response.data
          this.$refs.instructions_modal.show()
        }).catch(error => {
          console.log(error)
          this.$store.dispatch('setAlert', {
            $gettext: this.$gettext,
            message: { __all__: [this.alerts.cant_find_instructions] },
            variant: 'danger'
          })
        })
      }
    },
    checkBeforeSubmitting() {
      const unsavedTabs = Object.values(this.$store.state.form.tabs).filter(tab => [false, 'edited'].includes(tab.status))
      const incompleteQuestionnaire = Object.values(this.$store.state.form.tabs.questionaire_questions.form_fields).some(question => question.selected === null)
      if (unsavedTabs.length) {
        this.$store.dispatch('setAlert', {
          $gettext: this.$gettext,
          message: { __all__: [this.alerts.save_before_submit] },
          variant: 'danger'
        })
        return
      }
      if (incompleteQuestionnaire) {
        this.$store.dispatch('setAlert', {
          $gettext: this.$gettext,
          message: { __all__: [this.alerts.questionaire_beforeSubmit] },
          variant: 'danger'
        })
        return
      }
      this.currentTransition = 'submit'
      // this.$store.dispatch('doSubmissionTransition', { $gettext: this.$gettext, submission: this.submission, transition: 'submit' })
    },
    removeSubmission() {
      this.$store.dispatch('removeSubmission', {
        $gettext: this.$gettext,
        submissionUrl: this.submission
      }).then((result) => {
        if (result) {
          this.$router.push({ name: 'Dashboard' })
        }
      })
    }
  },
  watch: {
    '$language.current': {
      handler() {
        this.labels = getLabels(this.$gettext).common
        this.updateBreadcrumbs()
      }
    },
    '$store.state.current_submission.current_state': {
      handler() {
        this.updateBreadcrumbs()
      }
    }
  },
  data() {
    return {
      tabIndex: 0,
      modal_data: null,
      labels: getLabels(this.$gettext).common,
      alerts: getAlerts(this.$gettext),
      currentTransition: null
    }
  }
}

</script>
