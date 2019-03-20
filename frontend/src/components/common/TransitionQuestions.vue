<template>
	<div>
		<b-modal size="lg" ref="transition_modal" id="transition_modal">
				<Submit v-if="transition === 'submit'"/>
				<Process v-if="transition === 'process'"/>
				<Recall v-if="transition === 'recall'"/>
				<Finalize v-if="transition === 'finalize'"/>
				<Reinstate v-if="transition === 'unrecall_to_finalized'"/>

				<div slot="modal-footer">
					<b-btn class="mr-2" @click="$refs.transition_modal.hide()" variant="danger">
						<span v-translate>Close</span>
					</b-btn>
					<b-btn @click="doTransition" variant="success">Ok</b-btn>
				</div>
    </b-modal>
	</div>
</template>

<script>
import Submit from '@/components/common/transitionQuestions/Submit'
import Process from '@/components/common/transitionQuestions/Process'
import Recall from '@/components/common/transitionQuestions/Recall'
import Finalize from '@/components/common/transitionQuestions/Finalize'
import Reinstate from '@/components/common/transitionQuestions/Reinstate'

export default {
	props: {
		transition: String,
		submission: String
	},
	components: {
		Submit,
		Process,
		Recall,
		Finalize,
		Reinstate
	},
	data() {
		return {
			labels: {}
		}
	},
	mounted() {
		this.$root.$on('bv::modal::hide', (bvEvent, modalId) => {
			if (modalId === 'transition_modal') {
				this.$emit('removeTransition')
			}
		})
	},
	methods: {
		doTransition() {
			this.$store.dispatch('doSubmissionTransition', { $gettext: this.$gettext, submission: this.submission, transition: this.transition, noModal: true })
			this.$refs.transition_modal.hide()
		}
	},
	watch: {
		transition: {
			handler(val) {
				if (val !== null) {
					this.$refs.transition_modal.show()
				}
			}
		}
	}
}
</script>

