<template>
	<div>
		<b-modal size="lg" ref="transition_modal" id="transition_modal">
				<div>test</div>
				<div slot="modal-footer">
					<b-btn @click="$refs.transition_modal.hide()" variant="danger">
						<span v-translate>Close</span>
					</b-btn>
					<b-btn @click="doTransition" variant="success">Ok</b-btn>
				</div>
    </b-modal>
	</div>
</template>

<script>
export default {
	props: {
		transition: String,
		submission: String
	},

	data() {
		return {
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
			this.$store.dispatch('doSubmissionTransition', { $gettext: this.$gettext, submission: this.submission, transition: this.transition })
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

