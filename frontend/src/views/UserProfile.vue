<template>
<b-card class="col-md-4">
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
	<b-input-group class="mb-2" :prepend="$gettext('Party')">
		<input class="form-control" v-model="userProfile.party" :disabled="true" />
	</b-input-group>
	<b-input-group class="mb-2">
		<b-form-checkbox v-model="userProfile.is_read_only" :disabled="true">
		Is read only
		</b-form-checkbox>
	</b-input-group>
	<b-input-group class="mb-2">
		<b-form-checkbox v-model="userProfile.is_secretariat" :disabled="true">
		Is secretariat
		</b-form-checkbox>
	</b-input-group>
	<b-input-group class="mb-2">
		<b-button variant="primary" @click="save()">
			<i class="fa fa-floppy-o" aria-hidden="true"></i>
			&nbsp;
			<span v-translate>Save</span>
		</b-button>
	</b-input-group>
</b-card>
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
