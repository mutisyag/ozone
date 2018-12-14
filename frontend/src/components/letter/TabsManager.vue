<template>
  <div>
  <div class="breadcrumb custom">
    <small style="width: 30%;">
      <b-btn style="margin-right:.5rem" variant="info-outline" @click="createModalData"> <i class="fa fa-info fa-lg"></i></b-btn>
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
      <Save  v-if="$store.state.available_transitions.includes('submit')"  :data="$store.state.form" :submission="submission"></Save>
		<b-btn
			v-if="$store.state.available_transitions.includes('submit')"
			@click="checkBeforeSubmitting"
			variant="outline-success">
			Submit
		</b-btn>
		<b-btn
			variant="outline-primary"
			v-for="transition in availableTransitions"
			:key="transition"
			@click="$store.dispatch('doSubmissionTransition', {submission: submission, transition: transition})">
			{{labels[transition]}}
		</b-btn>

    </b-button-group>
  </div>

  <b-modal size="lg" ref="instructions_modal" id="instructions_modal">
    <div v-if="modal_data" v-html="modal_data"></div>
  </b-modal>

  <div class="form-wrapper" style="position: relative">
    <b-card style="margin-bottom: 5rem;" no-body>
		<b-tabs v-model="tabIndex" card>

          <b-tab title="Submission Info">
             <template slot="title">
              <div class="tab-title">
                Submission Info
              </div>
             </template>
			<SubmissionInfo ref="sub_info" :info="$store.state.form.tabs.sub_info" :tabId="0" />
          </b-tab>

           <b-tab title="Attachments">
			<template slot="title">
				<tab-title-with-loader :tab="$store.state.form.tabs.attachments" />
			</template>
            <attachments :tab="$store.state.form.tabs.attachments"></attachments>
          </b-tab>
        </b-tabs>

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
    </div>
    <Footer>
      <b-button-group class="actions mt-2 mb-2">
        <Save v-if="$store.state.available_transitions.includes('submit')" :data="$store.state.form" :submission="submission"></Save>
        <b-btn
          v-if="$store.state.available_transitions.includes('submit')"
          @click="checkBeforeSubmitting"
          variant="outline-success">
            Submit
        </b-btn>
		<b-btn
			variant="outline-primary"
			v-for="transition in availableTransitions"
			:key="transition"
			@click="$store.dispatch('doSubmissionTransition', {submission: submission, transition: transition})">
			{{labels[transition]}}
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
import SubmissionInfo from '@/components/common/SubmissionInfo.vue'
import Attachments from '@/components/common/Attachments.vue'
import { getInstructions } from '@/components/common/services/api'
import Save from '@/components/letter/Save'
import SubmissionHistory from '@/components/common/SubmissionHistory.vue'
import labels from '@/components/art7/dataDefinitions/labels'
import TabTitleWithLoader from '@/components/common/TabTitleWithLoader'

export default {
	components: {
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
	computed: {
		availableTransitions() {
			return this.$store.state.current_submission.available_transitions.filter(t => t !== 'submit')
		},
		selectedTab() {
			const { form } = this.$store.state
			const tab = form.tabs[form.formDetails.tabsDisplay[this.tabIndex]]
			const body = document.querySelector('body')
			if (tab.hasAssideMenu && !this.$store.getters.allowedChanges) {
				body.classList.add('aside-menu-lg-show')
			} else {
				body.classList.remove('aside-menu-lg-show')
			}
			return tab
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
			const fields = Object.keys(this.$store.state.form.tabs)
				.filter(tab => !['questionaire_questions', 'sub_info', 'attachments'].includes(tab))
				.map(tab => this.$store.state.form.tabs[tab].form_fields)
				.filter(arr => arr.length)
			if (!fields.length) {
				this.$store.dispatch('setAlert', {
					message: { __all__: ['You cannot submit and empty form'] },
					variant: 'danger'
				})
				return
			}

			const unsavedTabs = Object.values(this.$store.state.form.tabs).filter(tab => [false, 'edited'].includes(tab.status))
			if (unsavedTabs.length) {
				this.$store.dispatch('setAlert', {
					message: { __all__: ['Please save before submitting'] },
					variant: 'danger'
				})
				return
			}
			this.$store.dispatch('doSubmissionTransition', { submission: this.submission, transition: 'submit' })
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
			labels: labels.general
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
