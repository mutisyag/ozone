<template>
	<div>
		<div class="mb-2" v-if="$store.state.current_submission.current_state === 'finalized' || $store.state.current_submission.flag_superseded">
			<span class="color-green mr-3" v-if="$store.state.current_submission.current_state === 'finalized' && $store.state.current_submission.flag_valid">
				<i class="fa fa-check-square fa-lg mr-2"></i> <span v-translate>valid</span>
			</span>
			<span class="color-red mr-3" v-if="$store.state.current_submission.current_state === 'finalized' && !$store.state.current_submission.flag_valid">
				<i class="fa fa-window-close fa-lg mr-2"></i> <span v-translate>not valid</span>
			</span>
			<span v-b-tooltip.hover :title="superseded_tooltip" class="color-red mb-2" v-if="$store.state.current_submission.flag_superseded">
				<i class="fa fa-window-close fa-lg mr-2"></i> <span v-translate>superseded</span>
				&nbsp;<i style="color: black" class="fa fa-info-circle fa-sm"></i>
			</span>
		</div>
		<div>
			<span v-translate>Created by</span>
			{{$store.state.current_submission.filled_by_secretariat ? $gettext('secretariat'): $gettext('party')}}
			<span v-translate>at</span>
			{{$store.state.current_submission.created_at}}
		</div>
		<div class="mt-2">
			<span v-translate>Last changed by</span>
			{{$store.state.current_submission.filled_by_secretariat ? $gettext('secretariat'): $gettext('party')}}
			<span v-translate>at</span>
			{{$store.state.current_submission.updated_at}}
		</div>
	</div>
</template>

<script>
export default {
	data() {
		return {
			superseded_tooltip: this.$gettext('Another version has been submitted, overriding this one')
		}
	}
}
</script>
<style scoped>
	.color-green {
		color: green;
	}
	.color-red {
		color: red;
	}
</style>

