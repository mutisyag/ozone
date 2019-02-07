<template>
  <div>
  <div class="breadcrumb custom">
    <small style="width: 30%;">
		<b-btn style="margin-right:.5rem" variant="info-outline" @click="createModalData" v-show="!selectedTab.hideInfoButton">
			<i class="fa fa-info fa-lg"></i>
		</b-btn>
		<div v-html="selectedTab.detailsHtml"></div>
    </small>
    <div class="tab-title">
      <div  v-if='selectedTab.tooltipHtml' v-b-tooltip :title="selectedTab.tooltipHtml" >
        <span v-html="selectedTab.titleHtml"></span>
         <i style='margin-left: 5px' class="fa fa-info-circle fa-lg"></i>
      </div>
      <div v-else v-html="selectedTab.titleHtml"></div>
    </div>
   <b-button-group class="actions">
      <Save style="border-top-right-radius: .25em;border-bottom-right-radius: .25em;"  v-if="$store.state.available_transitions.includes('submit')"  :data="$store.state.form" :submission="submission"></Save>
    </b-button-group>
  </div>

  <b-modal size="lg" ref="instructions_modal" id="instructions_modal">
    <div v-if="modal_data" v-html="modal_data"></div>
  </b-modal>

  <div class="form-wrapper" style="position: relative">
    <b-card style="margin-bottom: 5rem;" no-body>
		<b-tabs v-model="tabIndex" card>
			<b-tab :title="$gettext('Submission Info')" active>
				<template slot="title">
				<div class="tab-title">
				<span v-translate>Submission Info</span>
				</div>
				</template>
			<SubmissionInfo ref="sub_info" :info="$store.state.form.tabs.sub_info" :tabId="0" />
			</b-tab>

			<b-tab :title="$gettext('Files')">
			<template slot="title">
				<tab-title-with-loader :tab="$store.state.form.tabs.files" />
			</template>
			<Files :tab="$store.state.form.tabs.files" />
			</b-tab>
			<b-tab v-for="tabId in tabsIdsWithAssideMenu" :key="tabId">
				<template slot="title">
					<tab-title-with-loader :tab="$store.state.form.tabs[tabId]" />
				</template>
				<FormTemplate :tabId="$store.state.form.formDetails.tabsDisplay.indexOf(tabId)" :tabIndex="tabIndex" :tabName="tabId" />
			</b-tab>
        </b-tabs>

        <div class="legend">
            <b><span v-translate>Legend:</span></b>
            <div>
              <div class="spinner">
                <div class="loader"></div>
              </div> - <span v-translate>Form is curently being saved</span>
            </div>
            <div>
              <i style="color: red;" class="fa fa-times-circle fa-lg"></i> - <span v-translate>Form save failed. Please check the validation</span>
            </div>
            <div>
              <i style="color: green;" class="fa fa-check-circle fa-lg"></i> - <span v-translate>Form was saved or no modifications were made. Current form data is synced with the data on the server</span>
            </div>
            <div>
              <i class="fa fa-edit fa-lg"></i> - <span v-translate>The form was edited and the data is not yet saved on the server. Please save before closing the form</span>
            </div>
        </div>
    </b-card>
    </div>
    <Footer style="display:inline">
			<Save class="actions mt-2 mb-2" v-if="$store.state.available_transitions.includes('submit')" :data="$store.state.form" :submission="submission"></Save>
			<b-button-group class="pull-right actions mt-2 mb-2">
				<b-btn
					v-if="$store.state.available_transitions.includes('submit')"
					@click="checkBeforeSubmitting"
					variant="outline-success">
						<span v-translate>Submit</span>
				</b-btn>
				<b-btn
					variant="outline-primary"
					v-for="transition in availableTransitions"
					:key="transition"
					@click="$store.dispatch('doSubmissionTransition', {$gettext, submission, transition})">
						<span>{{labels[transition]}}</span>
				</b-btn>
				<b-btn @click="$refs.history_modal.show()" variant="outline-info">
					<span v-translate>Versions</span>
				</b-btn>
				<b-btn @click="removeSubmission" v-if="$store.state.available_transitions.includes('submit')"  variant="outline-danger">
					<span v-translate>Delete Submission</span>
				</b-btn>
			</b-button-group>
    </Footer>

    <b-modal size="lg" ref="history_modal" id="history_modal"
             :title="$gettext('Submission versions')">
        <SubmissionHistory :history="$store.state.currentSubmissionHistory"
                           :currentVersion="$store.state.current_submission.version">
        </SubmissionHistory>
    </b-modal>
  </div>
</template>

<script>
import { Footer } from '@coreui/vue'
import SubmissionInfo from '@/components/common/SubmissionInfo.vue'
import Files from '@/components/common/Files'
import { getInstructions } from '@/components/common/services/api'
import Save from '@/components/letter/Save'
import SubmissionHistory from '@/components/common/SubmissionHistory.vue'
import { getLabels } from '@/components/art7/dataDefinitions/labels'
import TabTitleWithLoader from '@/components/common/TabTitleWithLoader'
import FormTemplate from '@/components/exemption/FormTemplate.vue'

export default {
	components: {
		SubmissionInfo,
		Files,
		Footer,
		Save,
		SubmissionHistory,
		TabTitleWithLoader,
		FormTemplate
	},
	props: {
		data: null,
		submission: String
	},
	data() {
		return {
			tabIndex: 0,
			modal_data: null,
			labels: getLabels(this.$gettext).common
		}
	},
	created() {
		this.$store.commit('updateBreadcrumbs', [this.$gettext('Dashboard'), this.$store.state.current_submission.obligation, this.$store.state.initialData.display.countries[this.$store.state.current_submission.party], this.$store.state.current_submission.reporting_period, `${this.$gettext('Version')} ${this.$store.state.current_submission.version}`])
	},
	computed: {
		availableTransitions() {
			return this.$store.state.current_submission.available_transitions.filter(t => t !== 'submit')
		},
		selectedTab() {
			const { form } = this.$store.state
			const tab = form.tabs[form.formDetails.tabsDisplay[this.tabIndex]]
			const body = document.querySelector('body')
			if (tab.hasAssideMenu && !this.$store.getters.isReadOnly) {
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
		createModalData() {
			const tabName = this.$store.state.form.formDetails.tabsDisplay[this.tabIndex]
			const formName = this.$route.name
			getInstructions(formName, tabName).then((response) => {
				this.modal_data = response.data
				this.$refs.instructions_modal.show()
			})
		},
		checkBeforeSubmitting() {
			const fields = Object.keys(this.$store.state.form.tabs)
				.filter(tab => !['questionaire_questions', 'sub_info', 'files'].includes(tab))
				.map(tab => this.$store.state.form.tabs[tab].form_fields)
				.filter(arr => arr.length)
			if (!fields.length) {
				this.$store.dispatch('setAlert', {
					$gettext: this.$gettext,
					message: { __all__: [this.$gettext('You cannot submit and empty form')] },
					variant: 'danger'
				})
				return
			}

			const unsavedTabs = Object.values(this.$store.state.form.tabs).filter(tab => [false, 'edited'].includes(tab.status))
			if (unsavedTabs.length) {
				this.$store.dispatch('setAlert', {
					$gettext: this.$gettext,
					message: { __all__: [this.$gettext('Please save before submitting')] },
					variant: 'danger'
				})
				return
			}
			this.$store.dispatch('doSubmissionTransition', { $gettext: this.$gettext, submission: this.submission, transition: 'submit' })
		},
		removeSubmission() {
			const r = confirm(this.$gettext('Deleting the submission is ireversible. Are you sure ?'))
			if (r === true) {
				this.$store.dispatch('removeSubmission', {
					$gettext: this.$gettext,
					submissionUrl: this.submission
				}).then(() => {
					this.$router.push({ name: 'Dashboard' })
				})
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
</style>
