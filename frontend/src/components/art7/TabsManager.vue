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
					<tab-title-with-loader :tab="$store.state.form.tabs.sub_info" />
				</template>
				<SubmissionInfo ref="sub_info" :flags_info="$store.state.form.tabs.flags" :info="$store.state.form.tabs.sub_info" :tabId="0" />
			</b-tab>

			<b-tab>
				<template slot="title">
					<tab-title-with-loader :tab="$store.state.form.tabs.questionaire_questions" />
				</template>
				<Questionnaire tabId="1" :info="$store.state.form.tabs.questionaire_questions" />
			</b-tab>

			<b-tab v-for="tabId in tabsIdsWithAssideMenu" :disabled="selectedDisplayTabs[$store.state.form.tabs[tabId].name] === null" :key="tabId">
				<template slot="title">
					<tab-title-with-loader :tab="$store.state.form.tabs[tabId]" />
				</template>
				<FormTemplate :hasDisabledFields="!selectedDisplayTabs[$store.state.form.tabs[tabId].name]" :tabId="$store.state.form.formDetails.tabsDisplay.indexOf(tabId)" :tabIndex="tabIndex" :tabName="tabId" />
			</b-tab>

			<b-tab :disabled="selectedDisplayTabs.has_emissions === null">
				<template slot="title">
					<tab-title-with-loader :tab="$store.state.form.tabs.has_emissions" />
				</template>
				<EmissionsTemplate :hasDisabledFields="!selectedDisplayTabs.has_emissions" tabId="7" ref="has_emissions"  :tabIndex="tabIndex"  tabName="has_emissions" />
			</b-tab>

			<b-tab >
				<template slot="title">
					<tab-title-with-loader :tab="$store.state.form.tabs.attachments" />
				</template>
				<Attachments :tab="$store.state.form.tabs.attachments"/>
			</b-tab>
		</b-tabs>
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
				<b-btn @click="removeSubmission" id="delete-button" v-if="$store.state.available_transitions.includes('submit')"  variant="outline-danger">
					<span v-translate>Delete Submission</span>
				</b-btn>
			</b-button-group>
    </Footer>

    <b-modal size="lg" ref="history_modal" id="history_modal"
             :title="$gettext('Submission versions')">
        <SubmissionHistory :history="$store.state.currentSubmissionHistory"
                           :currentVersion="$store.state.current_submission.version">
        </SubmissionHistory>
		<div slot="modal-footer">
			<b-btn @click="$refs.history_modal.hide()" variant="success">
				<span v-translate>Close</span>
			</b-btn>
		</div>
    </b-modal>
  </div>
</template>

<script>
import { Footer } from '@coreui/vue'
import Questionnaire from '@/components/art7/Questionnaire.vue'
import FormTemplate from '@/components/art7/FormTemplate.vue'
import EmissionsTemplate from '@/components/art7/EmissionsTemplate.vue'
import SubmissionInfo from '@/components/common/SubmissionInfo.vue'
import Attachments from '@/components/common/Attachments.vue'
import { getInstructions } from '@/components/common/services/api'
import Save from '@/components/art7/Save'
import SubmissionHistory from '@/components/common/SubmissionHistory.vue'
import { getLabels } from '@/components/art7/dataDefinitions/labels'
import TabTitleWithLoader from '@/components/common/TabTitleWithLoader'

export default {
	components: {
		Questionnaire,
		FormTemplate,
		EmissionsTemplate,
		SubmissionInfo,
		Attachments,
		Footer,
		Save,
		SubmissionHistory,
		TabTitleWithLoader
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
		updateBreadcrumbs() {
			this.$store.commit('updateBreadcrumbs', [this.$gettext('Dashboard'), this.labels[this.$route.name], this.$store.state.initialData.display.countries[this.$store.state.current_submission.party], this.$store.state.current_submission.reporting_period, `${this.$gettext('Version')} ${this.$store.state.current_submission.version}`])
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
						message: { __all__: [this.$gettext('Can\'t find instructions for current form')] },
						variant: 'danger'
					})
				})
			}
		},
		checkBeforeSubmitting() {
			const fields = Object.keys(this.$store.state.form.tabs)
				.filter(tab => !['questionaire_questions', 'sub_info', 'attachments'].includes(tab))
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
	},
	watch: {
		'$language.current': {
			handler() {
				this.labels = getLabels(this.$gettext).common
				this.updateBreadcrumbs()
			}
		}
	},
	data() {
		return {
			tabIndex: 0,
			modal_data: null,
			labels: getLabels(this.$gettext).common
		}
	}
}

</script>
