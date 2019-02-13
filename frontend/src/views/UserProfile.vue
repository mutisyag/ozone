<template>
<div class="row justify-content-center">
	<b-card class="col-md-6">
		<b-input-group class="mb-2" :prepend="$gettext('First name')">
			<input class="form-control" v-model="userProfile.first_name" />
		</b-input-group>
		<b-input-group class="mb-2" :prepend="$gettext('Last name')">
			<input class="form-control" v-model="userProfile.last_name" />
		</b-input-group>
		<b-input-group class="mb-2" :prepend="$gettext('Email')">
			<input class="form-control" v-model="userProfile.email" />
		</b-input-group>
		<b-input-group class="mb-2" :prepend="$gettext('Language')">
			<multiselect
					trackBy="value"
					label="text"
					v-model="userProfile.language"
					:options="availableLanguages" />
		</b-input-group>
		<b-input-group class="mb-2" :prepend="$gettext('User name')">
			<input class="form-control" v-model="userProfile.username" :disabled="true" />
		</b-input-group>
		<b-input-group class="mb-2" v-if="!userProfile.is_secretariat">
			<span v-translate>Party:</span>&nbsp;
			<b><span>{{userProfile.party}}</span></b>
		</b-input-group>
		<b-input-group class="mb-2">
			<span v-translate>Role:</span>&nbsp;
			<b>
				<span v-translate v-if="userProfile.is_secretariat">Secretariat</span>
				<span v-translate v-else>Party</span>
				&nbsp;<span v-translate v-if="userProfile.is_read_only">read-only</span>
			</b>
		</b-input-group>
	</b-card>
</div>
</template>

<script>
import Multiselect from '@/components/common/ModifiedMultiselect'
import { setLanguage } from '@/components/common/services/languageService'

export default {
	components: {
		Multiselect
	},
	data() {
		return {
			userProfile: null
		}
	},
	created() {
		this.$store.commit('updateBreadcrumbs', [this.$gettext('User profile')])
		console.log(this.$store.state.currentUser)
		this.userProfile = {
			...this.$store.state.currentUser
		}
		if (!this.userProfile.language) {
			this.userProfile.language = this.$language.current
		}
	},

	computed: {
		availableLanguages() {
			return Object.keys(this.$language.available)
				.map(key => ({ text: this.$language.available[key], value: key }))
		}
	},
	methods: {
		save() {
			this.$store.dispatch('updateCurrentUser', this.userProfile)
		}
	},
	watch: {
		'userProfile.language': {
			handler(newValue, oldValue) {
				if (newValue !== oldValue) {
					setLanguage(this.userProfile.language, this)
				}
			}
		}
	}
}
</script>
